from backend.app.agent.graph import build_graph
from backend.app.tracing.events import Trace
from langchain_core.messages import HumanMessage


def test_agent_creates_llm_trace():

    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is 10 + 5?"
                }
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    assert result["messages"]

    trace = result["trace"]

    assert isinstance(
        trace,
        Trace
    )

    event_types = [
        event.event_type
        for event in trace.events
    ]

    assert "RUN_STARTED" in event_types
    assert "LLM_REQUEST" in event_types
    assert "FINAL_RESPONSE" in event_types

    assert trace.status == "completed"


def test_agent_traces_final_response():
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is 125 * 37?"
                )
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    trace = result["trace"]

    event_types = [
        event.event_type
        for event in trace.events
    ]

    assert "FINAL_RESPONSE" in event_types
    assert trace.status == "completed"

    final_events = [
        event
        for event in trace.events
        if event.event_type == "FINAL_RESPONSE"
    ]

    assert len(final_events) == 1
    assert "4625" in final_events[0].data["response"]



def test_no_context_run_completes_trace():
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is the capital of France?"
                )
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    trace = result["trace"]

    assert trace.status == "completed"

    event_types = [
        event.event_type
        for event in trace.events
    ]

    assert "FINAL_RESPONSE" in event_types