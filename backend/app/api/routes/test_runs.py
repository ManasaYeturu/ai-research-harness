import uuid

from datetime import timedelta

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.tracing.events import Trace
from backend.app.database.trace_repository import save_trace


client = TestClient(app)


def test_list_runs_returns_runs(cleanup_trace):
    trace = Trace(
        run_id=str(uuid.uuid4())
    )

    trace.complete()
    save_trace(trace)

    cleanup_trace(trace.run_id)

    response = client.get("/runs")

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data

    matching_runs = [
        run
        for run in data["runs"]
        if run["run_id"] == trace.run_id
    ]

    assert len(matching_runs) == 1
    assert matching_runs[0]["status"] == "completed"


def test_list_runs_completed_filter(cleanup_trace):
    completed_trace = Trace(
        run_id=str(uuid.uuid4())
    )

    completed_trace.complete()
    save_trace(completed_trace)

    cleanup_trace(completed_trace.run_id)

    response = client.get(
        "/runs?status=completed"
    )

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data

    for run in data["runs"]:
        assert run["status"] == "completed"

    matching_runs = [
        run
        for run in data["runs"]
        if run["run_id"] == completed_trace.run_id
    ]

    assert len(matching_runs) == 1


def test_list_runs_with_limit():
    response = client.get(
        "/runs?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data
    assert len(data["runs"]) <= 2


def test_get_runs_summary_returns_dashboard_metrics():
    response = client.get("/runs/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_runs" in data
    assert "completed_runs" in data
    assert "failed_runs" in data
    assert "running_runs" in data

    assert "completion_rate" in data
    assert "average_execution_time_ms" in data

    assert "llm_calls" in data
    assert "average_llm_calls_per_run" in data

    assert "tool_calls" in data
    assert "tool_rejections" in data
    assert "tool_rejection_rate" in data


def test_list_runs_with_since_filter(cleanup_trace):
    trace = Trace(
        run_id=str(uuid.uuid4())
    )

    trace.complete()
    save_trace(trace)

    cleanup_trace(trace.run_id)

    since = (
        trace.started_at - timedelta(seconds=1)
    ).isoformat()

    response = client.get(
        f"/runs?since={since.replace('+', '%2B')}"
    )

    assert response.status_code == 200

    data = response.json()

    matching_runs = [
        run
        for run in data["runs"]
        if run["run_id"] == trace.run_id
    ]

    assert len(matching_runs) == 1


def test_list_runs_with_until_filter(cleanup_trace):
    trace = Trace(
        run_id=str(uuid.uuid4())
    )

    trace.complete()
    save_trace(trace)

    cleanup_trace(trace.run_id)

    until = (
        trace.started_at + timedelta(seconds=1)
    ).isoformat()

    response = client.get(
        f"/runs?until={until.replace('+', '%2B')}"
    )

    assert response.status_code == 200

    data = response.json()

    matching_runs = [
        run
        for run in data["runs"]
        if run["run_id"] == trace.run_id
    ]

    assert len(matching_runs) == 1


def test_list_runs_with_invalid_time_range(cleanup_trace):
    trace = Trace(
        run_id=str(uuid.uuid4())
    )

    trace.complete()
    save_trace(trace)

    cleanup_trace(trace.run_id)

    since = (
        trace.started_at + timedelta(seconds=10)
    ).isoformat()

    until = (
        trace.started_at - timedelta(seconds=10)
    ).isoformat()

    response = client.get(
        f"/runs?since={since.replace('+', '%2B')}"
        f"&until={until.replace('+', '%2B')}"
    )

    assert response.status_code == 400


def test_list_runs_combined_filter_and_limit():
    response = client.get(
        "/runs?status=completed&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data
    assert len(data["runs"]) <= 2

    for run in data["runs"]:
        assert run["status"] == "completed"


def test_list_runs_invalid_status():
    response = client.get(
        "/runs?status=invalid"
    )

    assert response.status_code == 400


def test_list_runs_invalid_limit():
    response = client.get(
        "/runs?limit=101"
    )

    assert response.status_code == 400


def test_get_run_returns_trace(cleanup_trace):
    trace = Trace(
        run_id=str(uuid.uuid4())
    )

    trace.add_event(
        "TEST_EVENT",
        {
            "message": "hello"
        }
    )

    trace.complete()
    save_trace(trace)

    cleanup_trace(trace.run_id)

    response = client.get(
        f"/runs/{trace.run_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["run_id"] == trace.run_id
    assert data["status"] == "completed"
    assert len(data["events"]) == 1
    assert data["events"][0]["event_type"] == "TEST_EVENT"


def test_get_unknown_run_returns_404():
    response = client.get(
        "/runs/non-existent-run"
    )

    assert response.status_code == 404