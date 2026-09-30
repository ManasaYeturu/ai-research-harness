from backend.app.database.connection import get_connection
from backend.app.database.trace_repository import save_trace
from backend.app.tracing.events import Trace


def test_save_trace(cleanup_trace):
    trace = Trace()

    trace.add_event(
        "RUN_STARTED",
        {}
    )

    trace.add_event(
        "LLM_REQUEST",
        {
            "model": "llama3.2:3b",
            "message_count": 1
        }
    )

    trace.complete()

    save_trace(trace)

    cleanup_trace(trace.run_id)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT run_id, status
                FROM runs
                WHERE run_id = %s
                """,
                (trace.run_id,)
            )

            run_result = cursor.fetchone()

            cursor.execute(
                """
                SELECT event_type, data
                FROM trace_events
                WHERE run_id = %s
                ORDER BY event_id
                """,
                (trace.run_id,)
            )

            event_results = cursor.fetchall()

        assert run_result is not None
        assert str(run_result[0]) == trace.run_id
        assert run_result[1] == "completed"

        assert len(event_results) == 2

        assert event_results[0][0] == "RUN_STARTED"

        assert event_results[1][0] == "LLM_REQUEST"
        assert event_results[1][1]["model"] == "llama3.2:3b"

    finally:
        connection.close()