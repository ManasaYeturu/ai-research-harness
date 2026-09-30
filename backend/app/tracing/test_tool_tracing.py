from langchain_core.messages import AIMessage

from backend.app.agent.graph import (
    build_graph,
    execute_tools_with_policy,
    tracer
)
from backend.app.tracing.events import Trace


def test_agent_creates_tool_trace():

    trace = tracer.start_trace()

    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {
                    "expression": "125 * 37"
                },
                "id": "test-tool-trace-1",
                "type": "tool_call"
            }
        ]
    )

    result = execute_tools_with_policy(
        {
            "messages": [
                tool_call
            ],
            "tool_call_count": 0,
            "no_relevant_context": False,
            "trace": trace
        }
    )

    returned_trace = result["trace"]

    assert isinstance(
        returned_trace,
        Trace
    )

    event_types = [
        event.event_type
        for event in returned_trace.events
    ]

    assert "TOOL_REQUEST" in event_types
    assert "TOOL_RESULT" in event_types

    assert event_types.index(
        "TOOL_REQUEST"
    ) < event_types.index(
        "TOOL_RESULT"
    )
def test_agent_traces_tool_rejection():

    trace = tracer.start_trace()

    invalid_tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {
                    "expression": "10 + abc"
                },
                "id": "test-rejection-1",
                "type": "tool_call"
            }
        ]
    )

    result = execute_tools_with_policy(
        {
            "messages": [
                invalid_tool_call
            ],
            "tool_call_count": 0,
            "no_relevant_context": False,
            "trace": trace
        }
    )

    returned_trace = result["trace"]

    assert isinstance(
        returned_trace,
        Trace
    )

    event_types = [
        event.event_type
        for event in returned_trace.events
    ]

    assert "TOOL_REJECTED" in event_types

    rejected_events = [
        event
        for event in returned_trace.events
        if event.event_type == "TOOL_REJECTED"
    ]

    assert len(rejected_events) == 1

    rejection = rejected_events[0]

    assert rejection.data["tool"] == "calculator"

    assert rejection.data["reason"] == "invalid_arguments"

    assert rejection.data["tool_call_id"] == "test-rejection-1"


def test_agent_traces_disallowed_tool():

    trace = tracer.start_trace()

    disallowed_tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "web_search",
                "args": {
                    "query": "PostgreSQL"
                },
                "id": "test-disallowed-1",
                "type": "tool_call"
            }
        ]
    )

    result = execute_tools_with_policy(
        {
            "messages": [
                disallowed_tool_call
            ],
            "tool_call_count": 0,
            "no_relevant_context": False,
            "trace": trace
        }
    )

    returned_trace = result["trace"]

    assert isinstance(
        returned_trace,
        Trace
    )

    rejected_events = [
        event
        for event in returned_trace.events
        if event.event_type == "TOOL_REJECTED"
    ]

    assert len(rejected_events) == 1

    rejection = rejected_events[0]

    assert rejection.data["tool"] == "web_search"

    assert rejection.data["reason"] == "tool_not_allowed"

    assert rejection.data["tool_call_id"] == "test-disallowed-1"

    assert result["messages"]

    assert (
        "not allowed"
        in result["messages"][0].content
    )


def test_agent_traces_tool_limit_rejection():

    trace = tracer.start_trace()

    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {
                    "expression": "10 + 5"
                },
                "id": "test-limit-1",
                "type": "tool_call"
            }
        ]
    )

    result = execute_tools_with_policy(
        {
            "messages": [
                tool_call
            ],
            "tool_call_count": 3,
            "no_relevant_context": False,
            "trace": trace
        }
    )

    returned_trace = result["trace"]

    rejected_events = [
        event
        for event in returned_trace.events
        if event.event_type == "TOOL_REJECTED"
    ]

    assert len(rejected_events) == 1

    rejection = rejected_events[0]

    assert rejection.data["tool"] == "calculator"

    assert rejection.data["reason"] == "tool_limit"

    assert rejection.data["tool_call_id"] == "test-limit-1"

    assert result["tool_call_count"] == 3

    assert result["messages"]

    assert (
        "Maximum tool-call limit reached"
        in result["messages"][0].content
    )