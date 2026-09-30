import psycopg


DATABASE_URL = (
    "host=localhost "
    "port=5432 "
    "dbname=ai_research_harness "
    "user=postgres "
    "password=1620"
)


def get_connection():
    return psycopg.connect(DATABASE_URL)