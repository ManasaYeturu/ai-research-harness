from datetime import datetime, timedelta, timezone

from backend.app.database.trace_repository import (
    save_trace,
    get_trace,
    mark_stale_runs_failed,
)
from backend.app.tracing.events import Trace


def test_mark_stale_run_failed(cleanup_trace):

    trace = Trace(
        started_at=datetime.now(timezone.utc) - timedelta(
            minutes=30
        )
    )

    trace.add_event(
        "RUN_STARTED",
        {}
    )

    save_trace(trace)

    cleanup_trace(trace.run_id)

    updated = mark_stale_runs_failed(
        max_age_minutes=10
    )

    assert updated >= 1

    loaded_trace = get_trace(
        trace.run_id
    )

    assert loaded_trace is not None
    assert loaded_trace.status == "failed"
    assert loaded_trace.completed_at is not None