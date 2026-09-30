from backend.app.evaluation.correctness import (
    evaluate_correctness
)


def test_correctness_accepts_equivalent_answer():

    result = evaluate_correctness(
        "A primary key uniquely identifies each row in a table.",
        "A primary key is a unique identifier for each row in a table."
    )

    assert result["passed"] is True
    assert result["reason"]


def test_correctness_rejects_incorrect_answer():

    result = evaluate_correctness(
        "A primary key uniquely identifies each row in a table.",
        "A primary key is used to store images and videos."
    )

    assert result["passed"] is False
    assert result["reason"]