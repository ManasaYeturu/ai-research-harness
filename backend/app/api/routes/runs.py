
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.app.config import STALE_RUN_MAX_AGE_MINUTES
from backend.app.database.trace_repository import (
    list_runs as list_runs_from_db,
    get_trace,
    get_run_summary,
    mark_stale_runs_failed
)


router = APIRouter(
    prefix="/runs",
    tags=["runs"]
)


SOURCE_PATTERN = re.compile(
    r"Source:\s*(?P<source>[^\n]+)\n"
    r"Chunk ID:\s*(?P<chunk_id>\d+)\n"
    r"Relevance Score:\s*(?P<score>\d+(?:\.\d+)?)\n"
    r"Content:\n"
    r"(?P<text>.*?)"
    r"(?=\n\nSource:\s*|\Z)",
    re.DOTALL
)


def extract_sources(events):
    sources = []

    for event in events:

        if event.event_type != "TOOL_RESULT":
            continue

        data = event.data

        if data.get("tool") != "document_search":
            continue

        result = data.get("result", "")

        if not result:
            continue

        matches = SOURCE_PATTERN.finditer(result)

        for match in matches:

            sources.append(
                {
                    "source": match.group("source").strip(),
                    "chunk_id": int(
                        match.group("chunk_id")
                    ),
                    "score": float(
                        match.group("score")
                    ),
                    "text": match.group("text").strip()
                }
            )

    return sources




@router.get("")
def list_runs(
    status: str | None = None,
    limit: int = 50,
    since: datetime | None = None,
    until: datetime | None = None
):


    mark_stale_runs_failed(
        max_age_minutes=STALE_RUN_MAX_AGE_MINUTES
    )



    allowed_statuses = {
        "completed",
        "failed",
        "running"
    }

    if (
        status is not None
        and status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. "
                "Allowed values: completed, failed, running."
            )
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100."
        )

    if since is not None and until is not None:
        if since > until:
            raise HTTPException(
                status_code=400,
                detail="Since must be earlier than until."
            )

    mark_stale_runs_failed()

    return {
        "runs": list_runs_from_db(
            status=status,
            limit=limit,
            since=since,
            until=until
        )
    }


@router.get("/summary")
def get_runs_summary():
    mark_stale_runs_failed(
        max_age_minutes=STALE_RUN_MAX_AGE_MINUTES
    )
    return get_run_summary()


@router.get("/{run_id}")
def get_run(run_id: str):
    trace = get_trace(run_id)

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    sources = extract_sources(
        trace.events
    )

    return {
        "run_id": trace.run_id,
        "started_at": trace.started_at,
        "completed_at": trace.completed_at,
        "status": trace.status,
        "metrics": trace.get_metrics(),
        "events": trace.events,
        "sources": sources
    }