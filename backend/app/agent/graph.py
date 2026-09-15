from langchain_ollama import ChatOllama

from langchain_core.messages import ToolMessage

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from .state import AgentState
from backend.app.tools.calculator import calculator
from backend.app.harness.policies import (
    validate_calculator_expression,
    can_execute_tool
)


MODEL_NAME = "llama3.2:3b"


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)

tools = [calculator]

llm_with_tools = llm.bind_tools(tools)


def call_model(state: AgentState):
    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


def execute_tools_with_policy(state: AgentState):

    last_message = state["messages"][-1]

    tool_messages = []

    tool_call_count = state.get("tool_call_count", 0)

    for tool_call in last_message.tool_calls:

        if not can_execute_tool(tool_call_count):

            tool_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution rejected by harness policy. "
                        "Maximum tool-call limit reached."
                    ),
                    tool_call_id=tool_call["id"]
                )
            )

            continue

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]

        if tool_name == "calculator":

            expression = tool_args.get("expression", "")

            is_valid = validate_calculator_expression(expression)

            if not is_valid:

                tool_messages.append(
                    ToolMessage(
                        content=(
                            "Tool execution rejected by harness policy. "
                            "The calculator only accepts mathematical "
                            "expressions."
                        ),
                        tool_call_id=tool_call_id
                    )
                )

                continue

        tool = {
            "calculator": calculator
        }.get(tool_name)

        if tool is None:

            tool_messages.append(
                ToolMessage(
                    content=f"Unknown tool: {tool_name}",
                    tool_call_id=tool_call_id
                )
            )

            continue

        result = tool.invoke(tool_args)

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call_id
            )
        )

        tool_call_count += 1

    return {
        "messages": tool_messages,
        "tool_call_count": tool_call_count
    }


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    tool_call_count = state.get("tool_call_count", 0)

    if not last_message.tool_calls:
        return END

    if not can_execute_tool(tool_call_count):
        return END

    return "tools"
    


def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("llm", call_model)

    graph.add_node(
        "tools",
        execute_tools_with_policy
    )

    graph.add_edge(
        START,
        "llm"
    )

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    graph.add_edge(
        "tools",
        "llm"
    )

    return graph.compile()