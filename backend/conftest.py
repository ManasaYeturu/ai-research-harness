import pytest

from backend.app.database.connection import get_connection


@pytest.fixture
def cleanup_trace():
    run_ids = set()

    def register(run_id):
        run_ids.add(run_id)

    yield register

    if not run_ids:
        return

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for run_id in run_ids:

                cursor.execute(
                    """
                    DELETE FROM trace_events
                    WHERE run_id = %s
                    """,
                    (run_id,)
                )

                cursor.execute(
                    """
                    DELETE FROM runs
                    WHERE run_id = %s
                    """,
                    (run_id,)
                )

        connection.commit()

    finally:
        connection.close()