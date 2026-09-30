import re
from uuid import uuid4

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    SystemMessage
)

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from backend.app.database.trace_repository import save_trace
from backend.app.harness.context import limit_context
from backend.app.harness.policies import (
    validate_tool_arguments,
    normalize_tool_arguments,
    can_execute_tool,
    is_tool_allowed
)
from backend.app.harness.validators import (
    validate_tool_result,
    normalize_final_answer,
    validate_final_answer
)
from backend.app.tools.calculator import calculator
from backend.app.tools.document_search import document_search
from backend.app.tracing.tracer import Tracer

from .prompts import SYSTEM_PROMPT
from .state import AgentState


MODEL_NAME = "llama3.2:3b"


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


tools = [
    calculator,
    document_search
]


llm_with_tools = llm.bind_tools(tools)


tracer = Tracer()


# ==========================================================
# LLM NODE
# ==========================================================

def call_model(
    state: AgentState
):
    messages = state["messages"]

    controlled_messages = limit_context(
        messages
    )

    model_messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        *controlled_messages
    ]

    if state.get("retrieved_context"):

        model_messages.append(
            SystemMessage(
                content=(
                    "RETRIEVED CONTEXT:\n"
                    f"{state['retrieved_context']}\n\n"
                    "Use only the retrieved context above when "
                    "answering the user's question. "
                    "Do not add facts, explanations, examples, "
                    "or assumptions that are not explicitly "
                    "supported by the retrieved context. "
                    "If the retrieved context does not contain "
                    "enough information to answer the question, "
                    "say that the information is not available "
                    "in the knowledge base."
                )
            )
        )

    trace = state.get(
        "trace"
    )

    if trace is not None:

        trace.add_event(
            "LLM_REQUEST",
            {
                "model": MODEL_NAME,
                "message_count": len(
                    model_messages
                )
            }
        )

    response = llm_with_tools.invoke(
        model_messages
    )

    return {
        "messages": [response],
        "trace": trace
    }


# ==========================================================
# TOOL EXECUTION NODE
# ==========================================================

def execute_tools_with_policy(
    state: AgentState
):
    last_message = state["messages"][-1]

    tool_messages = []

    tool_call_count = state.get(
        "tool_call_count",
        0
    )

    no_relevant_context = state.get(
        "no_relevant_context",
        False
    )

    retrieved_context = state.get(
        "retrieved_context",
        ""
    )

    trace = state.get(
        "trace"
    )

    for tool_call in last_message.tool_calls:

        tool_name = tool_call["name"]

        tool_args = normalize_tool_arguments(
            tool_call["name"],
            tool_call["args"]
        )

        tool_call_id = tool_call["id"]

        # --------------------------------------------------
        # 1. Check maximum tool-call limit
        # --------------------------------------------------

        if not can_execute_tool(
            tool_call_count
        ):

            if trace is not None:

                trace.add_event(
                    "TOOL_REJECTED",
                    {
                        "tool": tool_name,
                        "reason": "tool_limit",
                        "tool_call_id": tool_call_id
                    }
                )

            tool_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution rejected by "
                        "harness policy. Maximum "
                        "tool-call limit reached."
                    ),
                    tool_call_id=tool_call_id
                )
            )

            continue

        # --------------------------------------------------
        # 2. Check whether the tool is allowed
        # --------------------------------------------------

        if not is_tool_allowed(
            tool_name
        ):

            if trace is not None:

                trace.add_event(
                    "TOOL_REJECTED",
                    {
                        "tool": tool_name,
                        "reason": "tool_not_allowed",
                        "tool_call_id": tool_call_id
                    }
                )

            tool_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution rejected by "
                        "harness policy. "
                        f"Tool '{tool_name}' is not allowed."
                    ),
                    tool_call_id=tool_call_id
                )
            )

            continue

        # --------------------------------------------------
        # 3. Validate tool arguments
        # --------------------------------------------------

        if not validate_tool_arguments(
            tool_name,
            tool_args
        ):

            if trace is not None:

                trace.add_event(
                    "TOOL_REJECTED",
                    {
                        "tool": tool_name,
                        "reason": "invalid_arguments",
                        "arguments": tool_args,
                        "tool_call_id": tool_call_id
                    }
                )

            tool_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution rejected by "
                        "harness policy. "
                        f"Invalid arguments supplied "
                        f"to tool '{tool_name}'."
                    ),
                    tool_call_id=tool_call_id
                )
            )

            continue

        # --------------------------------------------------
        # 4. Resolve actual tool
        # --------------------------------------------------

        tool = {
            "calculator": calculator,
            "document_search": document_search
        }.get(
            tool_name
        )

        if tool is None:

            if trace is not None:

                trace.add_event(
                    "TOOL_REJECTED",
                    {
                        "tool": tool_name,
                        "reason": "unknown_tool",
                        "tool_call_id": tool_call_id
                    }
                )

            tool_messages.append(
                ToolMessage(
                    content=(
                        f"Unknown tool: {tool_name}"
                    ),
                    tool_call_id=tool_call_id
                )
            )

            continue

        # --------------------------------------------------
        # 5. Trace tool request
        # --------------------------------------------------

        if trace is not None:

            trace.add_event(
                "TOOL_REQUEST",
                {
                    "tool": tool_name,
                    "arguments": tool_args,
                    "tool_call_id": tool_call_id
                }
            )

        # --------------------------------------------------
        # 6. Execute tool
        # --------------------------------------------------

        try:

            result = tool.invoke(
                tool_args
            )

        except Exception as exc:

            if trace is not None:

                trace.add_event(
                    "TOOL_ERROR",
                    {
                        "tool": tool_name,
                        "error": str(exc),
                        "tool_call_id": tool_call_id
                    }
                )

            tool_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution failed. "
                        "The tool could not complete "
                        "the request."
                    ),
                    tool_call_id=tool_call_id
                )
            )

            tool_call_count += 1

            continue

        # --------------------------------------------------
        # 7. Validate tool result
        # --------------------------------------------------

        if not validate_tool_result(
            result
        ):

            if trace is not None:

                trace.add_event(
                    "TOOL_ERROR",
                    {
                        "tool": tool_name,
                        "error": "Invalid tool result",
                        "tool_call_id": tool_call_id
                    }
                )

            tool_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution failed. "
                        "The tool returned an invalid "
                        "result."
                    ),
                    tool_call_id=tool_call_id
                )
            )

            tool_call_count += 1

            continue

        # --------------------------------------------------
        # 8. Convert validated result to text
        # --------------------------------------------------

        result_text = str(
            result
        )

        # --------------------------------------------------
        # 9. Store retrieved document context
        # --------------------------------------------------

        if tool_name == "document_search":

            retrieved_context = result_text

        # --------------------------------------------------
        # 10. Trace successful tool result
        # --------------------------------------------------

        if trace is not None:

            trace.add_event(
                "TOOL_RESULT",
                {
                    "tool": tool_name,
                    "result": result_text,
                    "tool_call_id": tool_call_id
                }
            )

        # --------------------------------------------------
        # 11. Detect no relevant document context
        # --------------------------------------------------

        if (
            tool_name == "document_search"
            and result_text
            == "No relevant information was found."
        ):

            no_relevant_context = True

        # --------------------------------------------------
        # 12. Add validated result to agent context
        # --------------------------------------------------

        tool_messages.append(
            ToolMessage(
                content=result_text,
                tool_call_id=tool_call_id
            )
        )

        tool_call_count += 1

    return {
        "messages": tool_messages,
        "tool_call_count": tool_call_count,
        "no_relevant_context": no_relevant_context,
        "retrieved_context": retrieved_context,
        "trace": trace
    }


# ==========================================================
# FINAL RESPONSE NODE
# ==========================================================

def handle_final_response(
    state: AgentState
):

    last_message = state["messages"][-1]

    normalized_answer = normalize_final_answer(
        str(last_message.content)
    )

    # ------------------------------------------------------
    # FINAL ANSWER GUARDRAIL
    # ------------------------------------------------------

    if not validate_final_answer(
        normalized_answer
    ):

        controlled_answer = (
            "The agent could not generate a valid answer."
        )

        final_message = AIMessage(
            content=controlled_answer
        )

        trace = state.get(
            "trace"
        )

        if trace is not None:

            trace.add_event(
                "FINAL_RESPONSE_REJECTED",
                {
                    "reason": "invalid_final_answer"
                }
            )

            trace.add_event(
                "FINAL_RESPONSE",
                {
                    "response": controlled_answer
                }
            )

            trace.complete()

            save_trace(
                trace
            )

        return {
            "messages": [final_message],
            "trace": trace
        }

    # ------------------------------------------------------
    # VALID FINAL ANSWER
    # ------------------------------------------------------

    final_message = AIMessage(
        content=normalized_answer
    )

    trace = state.get(
        "trace"
    )

    if trace is not None:

        trace.add_event(
            "FINAL_RESPONSE",
            {
                "response": str(
                    final_message.content
                )
            }
        )

        trace.complete()

        save_trace(
            trace
        )

    return {
        "messages": [final_message],
        "trace": trace
    }


# ==========================================================
# NO RELEVANT CONTEXT NODE
# ==========================================================

def handle_no_relevant_context(
    state: AgentState
):

    message = AIMessage(
        content=(
            "I couldn't find relevant information "
            "in the knowledge base to answer that question."
        )
    )

    trace = state.get(
        "trace"
    )

    if trace is not None:

        trace.add_event(
            "FINAL_RESPONSE",
            {
                "response": str(
                    message.content
                )
            }
        )

        trace.complete()

        save_trace(
            trace
        )

    return {
        "messages": [message],
        "trace": trace
    }


# ==========================================================
# NORMALIZE MODEL OUTPUT
# ==========================================================

def normalize_model_output(
    state: AgentState
):
    """
    Detect a structured function-call envelope that the
    local LLM sometimes returns as plain text instead of
    LangChain tool_calls.

    The model may produce invalid JSON because it places
    literal newlines inside the description field.

    Therefore, only the specific fields required by the
    harness are extracted instead of attempting to repair
    arbitrary JSON.
    """

    last_message = state["messages"][-1]

    # The model already produced proper tool_calls.
    if last_message.tool_calls:
        return {}

    content = last_message.content

    if not isinstance(
        content,
        str
    ):
        return {}

    content = content.strip()

    if '"type":"function"' not in content:
        return {}

    if '"function"' not in content:
        return {}

    # ------------------------------------------------------
    # Extract tool name
    # ------------------------------------------------------

    tool_name_match = re.search(
        r'"name"\s*:\s*"([^"]+)"',
        content
    )

    if not tool_name_match:
        return {}

    tool_name = tool_name_match.group(
        1
    )

    if tool_name not in {
        "calculator",
        "document_search"
    }:
        return {}

    # ------------------------------------------------------
    # Extract tool arguments
    # ------------------------------------------------------

    if tool_name == "document_search":

        query_match = re.search(
            r'"query"\s*:\s*"([^"]*)"',
            content
        )

        if not query_match:
            return {}

        parameters = {
            "query": query_match.group(1)
        }

    elif tool_name == "calculator":

        expression_match = re.search(
            r'"expression"\s*:\s*"([^"]*)"',
            content
        )

        if not expression_match:
            return {}

        parameters = {
            "expression": expression_match.group(1)
        }

    else:
        return {}

    # ------------------------------------------------------
    # Create normalized tool call
    # ------------------------------------------------------

    tool_call = {
        "name": tool_name,
        "args": parameters,
        "id": str(uuid4()),
        "type": "tool_call"
    }

    normalized_message = AIMessage(
        content="",
        tool_calls=[tool_call]
    )

    trace = state.get(
        "trace"
    )

    if trace is not None:

        trace.add_event(
            "TOOL_CALL_NORMALIZED",
            {
                "tool": tool_name,
                "arguments": parameters
            }
        )

    return {
        "messages": [normalized_message],
        "trace": trace
    }


# ==========================================================
# ROUTING: LLM → TOOLS / FINAL
# ==========================================================

def should_continue(
    state: AgentState
):

    last_message = state["messages"][-1]

    tool_call_count = state.get(
        "tool_call_count",
        0
    )

    if not last_message.tool_calls:
        return "final"

    if not can_execute_tool(
        tool_call_count
    ):
        return "final"

    return "tools"


# ==========================================================
# ROUTING: TOOLS → LLM / NO CONTEXT
# ==========================================================

def route_after_tools(
    state: AgentState
):

    no_context = state.get(
        "no_relevant_context",
        False
    )

    if no_context:
        return "no_context"

    return "llm"


# ==========================================================
# TRACE INITIALIZATION
# ==========================================================

def initialize_trace(
    state: AgentState
):

    trace = tracer.start_trace()

    trace.add_event(
        "RUN_STARTED",
        {}
    )

    return {
        "trace": trace
    }


# ==========================================================
# BUILD GRAPH
# ==========================================================

def build_graph():

    graph = StateGraph(
        AgentState
    )

    # ------------------------------------------------------
    # Nodes
    # ------------------------------------------------------

    graph.add_node(
        "initialize_trace",
        initialize_trace
    )

    graph.add_node(
        "llm",
        call_model
    )

    graph.add_node(
        "normalize_model_output",
        normalize_model_output
    )

    graph.add_node(
        "tools",
        execute_tools_with_policy
    )

    graph.add_node(
        "final",
        handle_final_response
    )

    graph.add_node(
        "no_context",
        handle_no_relevant_context
    )

    # ------------------------------------------------------
    # Entry point
    # ------------------------------------------------------

    graph.add_edge(
        START,
        "initialize_trace"
    )

    graph.add_edge(
        "initialize_trace",
        "llm"
    )

    # ------------------------------------------------------
    # LLM → Normalize → Tools / Final
    # ------------------------------------------------------

    graph.add_edge(
        "llm",
        "normalize_model_output"
    )

    graph.add_conditional_edges(
        "normalize_model_output",
        should_continue,
        {
            "tools": "tools",
            "final": "final"
        }
    )

    # ------------------------------------------------------
    # Tools → LLM / No Context
    # ------------------------------------------------------

    graph.add_conditional_edges(
        "tools",
        route_after_tools,
        {
            "llm": "llm",
            "no_context": "no_context"
        }
    )

    # ------------------------------------------------------
    # Final → End
    # ------------------------------------------------------

    graph.add_edge(
        "final",
        END
    )

    # ------------------------------------------------------
    # No Context → End
    # ------------------------------------------------------

    graph.add_edge(
        "no_context",
        END
    )

    # ------------------------------------------------------
    # Compile graph
    # ------------------------------------------------------

    compiled_graph = graph.compile()

    return compiled_graph