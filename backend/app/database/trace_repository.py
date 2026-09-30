from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from backend.app.tracing.events import Trace
from backend.app.database.connection import get_connection



def mark_stale_runs_failed(
    max_age_minutes: int = 10
) -> int:
    """
    Mark long-running traces as failed.

    A run is considered stale when:
    - status is still 'running'
    - started_at is older than max_age_minutes

    Returns the number of runs updated.
    """

    cutoff_time = datetime.now(timezone.utc) - timedelta(
        minutes=max_age_minutes
    )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE runs
                SET
                    status = 'failed',
                    completed_at = %s
                WHERE
                    status = 'running'
                    AND started_at < %s
                """,
                (
                    datetime.now(timezone.utc),
                    cutoff_time
                )
            )

            updated_count = cursor.rowcount

        connection.commit()

        return updated_count

    finally:
        connection.close()


def save_run(trace):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO runs (
                    run_id,
                    started_at,
                    completed_at,
                    status
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    trace.run_id,
                    trace.started_at,
                    trace.completed_at,
                    trace.status
                )
            )

        connection.commit()

    finally:
        connection.close()


def save_trace_events(trace):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for event in trace.events:
                cursor.execute(
                    """
                    INSERT INTO trace_events (
                        run_id,
                        event_type,
                        data,
                        timestamp
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        trace.run_id,
                        event.event_type,
                        Jsonb(event.data),
                        event.timestamp
                    )
                )

        connection.commit()

    finally:
        connection.close()


def save_trace(trace):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO runs (
                    run_id,
                    started_at,
                    completed_at,
                    status
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    trace.run_id,
                    trace.started_at,
                    trace.completed_at,
                    trace.status
                )
            )

            for event in trace.events:
                cursor.execute(
                    """
                    INSERT INTO trace_events (
                        run_id,
                        event_type,
                        data,
                        timestamp
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        trace.run_id,
                        event.event_type,
                        Jsonb(event.data),
                        event.timestamp
                    )
                )

        connection.commit()

    finally:
        connection.close()


def get_trace(run_id: str):
    try:
        UUID(run_id)
    except ValueError:
        return None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    run_id,
                    started_at,
                    completed_at,
                    status
                FROM runs
                WHERE run_id = %s
                """,
                (run_id,)
            )

            run_result = cursor.fetchone()

            if run_result is None:
                return None

            trace = Trace(
                run_id=str(run_result[0]),
                started_at=run_result[1],
                completed_at=run_result[2],
                status=run_result[3]
            )

            cursor.execute(
                """
                SELECT
                    event_type,
                    data,
                    timestamp
                FROM trace_events
                WHERE run_id = %s
                ORDER BY event_id
                """,
                (run_id,)
            )

            event_results = cursor.fetchall()

            for event_type, data, timestamp in event_results:
                event = trace.add_event(
                    event_type,
                    data
                )

                event.timestamp = timestamp

            return trace

    finally:
        connection.close()


def list_runs(
    status: str | None = None,
    limit: int = 50,
    since=None,
    until=None
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            query = """
                SELECT
                    run_id,
                    started_at,
                    completed_at,
                    status
                FROM runs
            """

            conditions = []
            parameters = []

            if status is not None:
                conditions.append(
                    "status = %s"
                )

                parameters.append(status)

            if since is not None:
                conditions.append(
                    "started_at >= %s"
                )

                parameters.append(since)

            if until is not None:
                conditions.append(
                    "started_at <= %s"
                )

                parameters.append(until)

            if conditions:
                query += (
                    " WHERE "
                    + " AND ".join(conditions)
                )

            query += """
                ORDER BY started_at DESC
                LIMIT %s
            """

            parameters.append(limit)

            cursor.execute(
                query,
                tuple(parameters)
            )

            results = cursor.fetchall()

            return [
                {
                    "run_id": str(run_id),
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "status": status
                }
                for (
                    run_id,
                    started_at,
                    completed_at,
                    status
                ) in results
            ]

    finally:
        connection.close()


def get_run_summary():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_runs,

                    COUNT(*) FILTER (
                        WHERE status = 'completed'
                    ) AS completed_runs,

                    COUNT(*) FILTER (
                        WHERE status = 'failed'
                    ) AS failed_runs,

                    COUNT(*) FILTER (
                        WHERE status = 'running'
                    ) AS running_runs,

                    AVG(
                        EXTRACT(
                            EPOCH FROM (
                                completed_at - started_at
                            )
                        ) * 1000
                    ) FILTER (
                        WHERE status = 'completed'
                        AND completed_at IS NOT NULL
                    ) AS average_execution_time_ms

                FROM runs
                """
            )

            run_summary = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE event_type = 'LLM_REQUEST'
                    ) AS llm_calls,

                    COUNT(*) FILTER (
                        WHERE event_type = 'TOOL_REQUEST'
                    ) AS tool_calls,

                    COUNT(*) FILTER (
                        WHERE event_type = 'TOOL_REJECTED'
                    ) AS tool_rejections

                FROM trace_events
                """
            )

            event_summary = cursor.fetchone()

            total_runs = run_summary[0]
            completed_runs = run_summary[1]

            llm_calls = event_summary[0]
            tool_calls = event_summary[1]
            tool_rejections = event_summary[2]

            completion_rate = (
                (completed_runs / total_runs) * 100
                if total_runs > 0
                else 0
            )

            average_llm_calls_per_run = (
                llm_calls / total_runs
                if total_runs > 0
                else 0
            )

            tool_rejection_rate = (
                (tool_rejections / tool_calls) * 100
                if tool_calls > 0
                else 0
            )

            return {
                "total_runs": total_runs,
                "completed_runs": completed_runs,
                "failed_runs": run_summary[2],
                "running_runs": run_summary[3],

                "completion_rate": completion_rate,

                "average_execution_time_ms": (
                    float(run_summary[4])
                    if run_summary[4] is not None
                    else None
                ),

                "llm_calls": llm_calls,
                "average_llm_calls_per_run": (
                    average_llm_calls_per_run
                ),

                "tool_calls": tool_calls,
                "tool_rejections": tool_rejections,

                "tool_rejection_rate": tool_rejection_rate,
            }

    finally:
        connection.close()