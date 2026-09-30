from backend.app.database.connection import get_connection
from backend.app.database.trace_repository import save_run, save_trace_events
from backend.app.tracing.events import Trace



def test_save_trace_events():
    trace = Trace()
    save_run(trace)

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

    save_trace_events(trace)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT event_type, data
                FROM trace_events
                WHERE run_id = %s
                ORDER BY event_id
                """,
                (trace.run_id,)
            )

            results = cursor.fetchall()

        assert len(results) == 2

        assert results[0][0] == "LLM_REQUEST"
        assert results[0][1]["model"] == "llama3.2:3b"

        assert results[1][0] == "FINAL_RESPONSE"
        assert results[1][1]["response"] == "Test response"

    finally:
        connection.close()