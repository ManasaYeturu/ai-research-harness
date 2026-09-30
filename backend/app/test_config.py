from backend.app.config import STALE_RUN_MAX_AGE_MINUTES


def test_stale_run_max_age_minutes():
    assert STALE_RUN_MAX_AGE_MINUTES == 10