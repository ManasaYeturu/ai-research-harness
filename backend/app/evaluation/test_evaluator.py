
from backend.app.evaluation.evaluator import (
    load_evaluation_dataset,
    run_evaluation_case,
    evaluate_answer,
    evaluate_required_keywords,
    run_evaluation
)



def test_run_evaluation():

    results = run_evaluation(
        "datasets/basic_tasks.jsonl"
    )

    assert len(results) == 5

    for result in results:
        assert "id" in result
        assert "question" in result
        assert "expected_answer" in result
        assert "actual_answer" in result
        assert "passed" in result
        assert "run_id" in result
        assert "retrieved_context" in result
        assert "faithfulness_passed" in result
        assert "faithfulness_reason" in result


def test_evaluate_answer():

    assert evaluate_answer(
        "PostgreSQL is a database.",
        "PostgreSQL is a database."
    )

    assert not evaluate_answer(
        "PostgreSQL is a database.",
        "PostgreSQL is a programming language."
    )


def test_load_evaluation_dataset():

    test_cases = load_evaluation_dataset(
        "datasets/basic_tasks.jsonl"
    )

    assert len(test_cases) == 5

    assert test_cases[0]["id"] == "basic_001"

    assert (
        test_cases[0]["question"]
        == "What is PostgreSQL?"
    )

    assert test_cases[4]["id"] == "basic_005"


def test_run_evaluation_case():

    test_cases = load_evaluation_dataset(
        "datasets/basic_tasks.jsonl"
    )

    result = run_evaluation_case(
        test_cases[0]
    )

    assert result["id"] == "basic_001"
    assert result["question"] == "What is PostgreSQL?"
    assert result["expected_answer"]
    assert result["actual_answer"]
    assert result["run_id"]

def test_evaluate_required_keywords():

    result = evaluate_required_keywords(
        "A primary key uniquely identifies each row in a table.",
        [
            "primary key",
            "uniquely",
            "row",
            "table"
        ]
    )

    assert result["passed"] is True
    assert result["missing_keywords"] == []


def test_evaluate_required_keywords_detects_missing_content():

    result = evaluate_required_keywords(
        "A primary key identifies records.",
        [
            "primary key",
            "row",
            "table"
        ]
    )

    assert result["passed"] is False
    assert "row" in result["missing_keywords"]
    assert "table" in result["missing_keywords"]