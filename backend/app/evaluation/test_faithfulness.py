from backend.app.evaluation.faithfulness import (
    evaluate_faithfulness
)


def test_faithfulness_accepts_supported_answer():

    context = """
    PostgreSQL supports tables, primary keys, foreign keys,
    constraints, indexes, views, functions, and transactions.
    """

    answer = """
    PostgreSQL supports primary keys and foreign keys.
    """

    result = evaluate_faithfulness(
        context,
        answer
    )

    assert result["passed"] is True
    assert result["reason"]


def test_faithfulness_rejects_unsupported_claim():

    context = """
    Indexes can improve query performance by allowing PostgreSQL
    to locate rows more efficiently.
    """

    answer = """
    Indexes improve query performance and PostgreSQL automatically
    maintains them using the VACUUM command.
    """

    result = evaluate_faithfulness(
        context,
        answer
    )

    assert result["passed"] is False
    assert result["reason"]


def test_faithfulness_rejects_mixed_supported_and_unsupported_claims():

    context = """
    Indexes can improve query performance by allowing PostgreSQL
    to locate rows more efficiently.
    """

    answer = """
    Indexes improve query performance and automatically encrypt
    all database records.
    """

    result = evaluate_faithfulness(
        context,
        answer
    )

    assert result["passed"] is False
    assert result["reason"]