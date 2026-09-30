from backend.app.tracing.tracer import Tracer


def test_start_trace_creates_trace():

    tracer = Tracer()

    trace = tracer.start_trace()

    assert trace.run_id
    assert trace.status == "running"


def test_started_trace_is_stored():

    tracer = Tracer()

    trace = tracer.start_trace()

    stored_trace = tracer.get_trace(
        trace.run_id
    )

    assert stored_trace is trace


def test_unknown_trace_returns_none():

    tracer = Tracer()

    result = tracer.get_trace(
        "unknown-run-id"
    )

    assert result is None


def test_multiple_traces_have_unique_ids():

    tracer = Tracer()

    trace_one = tracer.start_trace()
    trace_two = tracer.start_trace()

    assert trace_one.run_id != trace_two.run_id