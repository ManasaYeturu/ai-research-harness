import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "host=localhost port=5432 dbname=ai_research_harness user=postgres"
)


STALE_RUN_MAX_AGE_MINUTES = int(
    os.getenv(
        "STALE_RUN_MAX_AGE_MINUTES",
        "10"
    )
)