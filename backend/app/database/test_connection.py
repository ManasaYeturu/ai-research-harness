from backend.app.database.connection import get_connection


def test_database_connection():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        assert result == (1,)

    finally:
        connection.close()