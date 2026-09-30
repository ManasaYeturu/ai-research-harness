from backend.app.database.connection import get_connection
from backend.app.database.trace_repository import save_run
from backend.app.tracing.events import Trace


def test_save_run():
    trace = Trace()

    save_run(trace)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT run_id, started_at, status
                FROM runs
                WHERE run_id = %s
                """,
                (trace.run_id,)
            )

            result = cursor.fetchone()

        assert result is not None
        assert str(result[0]) == trace.run_id
        assert result[1] == trace.started_at
        assert result[2] == trace.status

    finally:
        connection.close()