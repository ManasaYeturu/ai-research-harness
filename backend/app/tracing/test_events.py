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