from backend.app.tracing.events import (
    Trace,
    TraceEvent
)


def test_trace_has_unique_run_id():

    trace = Trace()

    assert trace.run_id
    assert isinstance(trace.run_id, str)


def test_trace_starts_as_running():

    trace = Trace()

    assert trace.status == "running"


def test_trace_starts_with_no_events():

    trace = Trace()

    assert trace.events == []


def test_add_event():

    trace = Trace()

    event = trace.add_event(
        "TOOL_SELECTED",
        {
            "tool": "calculator"
        }
    )

    assert isinstance(
        event,
        TraceEvent
    )

    assert event.event_type == "TOOL_SELECTED"

    assert event.data["tool"] == "calculator"

    assert len(trace.events) == 1

def test_trace_can_be_completed():

    trace = Trace()

    trace.complete()

    assert trace.status == "completed"


def test_trace_can_be_marked_failed():

    trace = Trace()

    trace.fail()

    assert trace.status == "failed"



def test_trace_completion_sets_completed_at():

    trace = Trace()

    assert trace.completed_at is None

    trace.complete()

    assert trace.completed_at is not None


def test_trace_failure_sets_completed_at():

    trace = Trace()

    assert trace.completed_at is None

    trace.fail()

    assert trace.completed_at is not None


def test_event_has_utc_timestamp():

    trace = Trace()

    event = trace.add_event(
        "TOOL_SELECTED",
        {
            "tool": "calculator"
        }
    )

    assert event.timestamp is not None
    assert event.timestamp.tzinfo is not None


def test_trace_metrics():

    trace = Trace()

    trace.add_event("LLM_REQUEST")
    trace.add_event("LLM_REQUEST")

    trace.add_event(
        "TOOL_REQUEST",
        {"tool": "calculator"}
    )

    trace.add_event(
        "TOOL_RESULT",
        {"tool": "calculator"}
    )

    trace.add_event(
        "TOOL_REJECTED",
        {"tool": "document_search"}
    )

    trace.add_event(
        "TOOL_ERROR",
        {"tool": "calculator"}
    )

    trace.add_event(
        "FINAL_RESPONSE_REJECTED"
    )

    metrics = trace.get_metrics()

    assert metrics["llm_calls"] == 2
    assert metrics["tool_calls"] == 1
    assert metrics["tool_results"] == 1
    assert metrics["tool_rejections"] == 1
    assert metrics["tool_errors"] == 1
    assert metrics["final_response_rejections"] == 1


def test_execution_time_is_none_while_running():

    trace = Trace()

    metrics = trace.get_metrics()

    assert metrics["execution_time_ms"] is None


def test_execution_time_is_available_after_completion():

    trace = Trace()

    trace.complete()

    metrics = trace.get_metrics()

    assert metrics["execution_time_ms"] is not None
    assert metrics["execution_time_ms"] >= 0