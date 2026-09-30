import os

from dotenv import load_dotenv


load_dotenv()


STALE_RUN_MAX_AGE_MINUTES = int(
    os.getenv(
        "STALE_RUN_MAX_AGE_MINUTES",
        "10"
    )
)