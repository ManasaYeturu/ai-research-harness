from langchain_core.messages import AIMessage, ToolMessage

from backend.app.agent import graph
from backend.app.tracing.events import Trace


from langchain_core.messages import AIMessage
from backend.app.agent.graph import execute_tools_with_policy
from backend.app.tracing.events import Trace


class FailingTool:

    def invoke(self, tool_args):
        raise RuntimeError("Qdrant connection failed")


def test_tool_execution_failure_is_handled(monkeypatch):

    monkeypatch.setattr(
        graph,
        "document_search",
        FailingTool()
    )

    trace = Trace()

    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "document_search",
                        "args": {
                            "query": "What is PostgreSQL?"
                        },
                        "id": "test-tool-call-1",
                        "type": "tool_call"
                    }
                ]
            )
        ],
        "tool_call_count": 0,
        "no_relevant_context": False,
        "retrieved_context": "",
        "trace": trace
    }

    result = graph.execute_tools_with_policy(state)

    # Failed execution is still counted.
    assert result["tool_call_count"] == 1

    # Harness returns a controlled ToolMessage.
    tool_message = result["messages"][0]

    assert isinstance(
        tool_message,
        ToolMessage
    )

    assert (
        "Tool execution failed"
        in tool_message.content
    )

    # Harness records the runtime failure.
    error_events = [
        event
        for event in trace.events
        if event.event_type == "TOOL_ERROR"
    ]

    assert len(error_events) == 1

    error_event = error_events[0]

    assert error_event.data["tool"] == "document_search"

    assert trace.get_metrics()["tool_errors"] == 1

    assert (
        error_event.data["error"]
        == "Qdrant connection failed"
    )





def test_tool_execution_limit_is_enforced():
    trace = Trace()

    message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {"expression": "10 + 1"},
                "id": "tool-call-1",
                "type": "tool_call",
            },
            {
                "name": "calculator",
                "args": {"expression": "10 + 2"},
                "id": "tool-call-2",
                "type": "tool_call",
            },
            {
                "name": "calculator",
                "args": {"expression": "10 + 3"},
                "id": "tool-call-3",
                "type": "tool_call",
            },
            {
                "name": "calculator",
                "args": {"expression": "10 + 4"},
                "id": "tool-call-4",
                "type": "tool_call",
            },
        ],
    )

    result = execute_tools_with_policy(
        {
            "messages": [message],
            "tool_call_count": 0,
            "no_relevant_context": False,
            "trace": trace,
        }
    )

    # Only the first three tool calls are allowed.
    assert result["tool_call_count"] == 3

    # All four tool calls receive a ToolMessage,
    # but the fourth one must be a rejection.
    assert len(result["messages"]) == 4

    rejected_events = [
        event
        for event in trace.events
        if event.event_type == "TOOL_REJECTED"
    ]

    assert len(rejected_events) == 1

    rejected_event = rejected_events[0]

    assert rejected_event.data["tool"] == "calculator"
    assert rejected_event.data["reason"] == "tool_limit"
    assert rejected_event.data["tool_call_id"] == "tool-call-4"

    assert (
        result["messages"][-1].content
        == (
            "Tool execution rejected by harness policy. "
            "Maximum tool-call limit reached."
        )
    )

    assert trace.get_metrics()["tool_rejections"] == 1