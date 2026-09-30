from backend.app.database.trace_repository import (
    save_trace,
    get_trace
)

from backend.app.tracing.events import Trace


def test_get_trace(cleanup_trace):
    trace = Trace()

    trace.add_event(
        "LLM_REQUEST",
        {
            "model": "llama3.2:3b",
            "message_count": 1
        }
    )

    trace.add_event(
        "FINAL_RESPONSE",
        {
            "response": "Test response"
        }
    )

    trace.complete()

    save_trace(trace)

    cleanup_trace(trace.run_id)

    loaded_trace = get_trace(
        trace.run_id
    )

    assert loaded_trace is not None

    assert loaded_trace.run_id == trace.run_id
    assert loaded_trace.started_at == trace.started_at
    assert loaded_trace.status == "completed"

    assert len(loaded_trace.events) == 2

    assert loaded_trace.events[0].event_type == "LLM_REQUEST"

    assert (
        loaded_trace.events[0].data["model"]
        == "llama3.2:3b"
    )

    assert loaded_trace.events[1].event_type == "FINAL_RESPONSE"

    assert (
        loaded_trace.events[1].data["response"]
        == "Test response"
    )


def test_get_unknown_trace_returns_none():
    result = get_trace(
        "00000000-0000-0000-0000-000000000000"
    )

    assert result is None