import pytest

from backend.app.evaluation.relevance import (
    evaluate_relevance
)


def test_relevant_context():

    result = evaluate_relevance(
        question="What is a primary key?",
        retrieved_context=(
            "A primary key uniquely identifies "
            "each row in a table."
        ),
        expected_keywords=[
            "primary key",
            "row",
            "table"
        ]
    )

    assert result["relevant"] is True

    assert result["matched_keywords"] == [
        "primary key",
        "row",
        "table"
    ]

    assert result["missing_keywords"] == []


def test_irrelevant_context():

    result = evaluate_relevance(
        question="What is quantum computing?",
        retrieved_context=(
            "PostgreSQL is an open-source "
            "object-relational database."
        ),
        expected_keywords=[
            "quantum computing"
        ]
    )

    assert result["relevant"] is False

    assert result["matched_keywords"] == []

    assert result["missing_keywords"] == [
        "quantum computing"
    ]


def test_partially_relevant_context():

    result = evaluate_relevance(
        question="What is a primary key?",
        retrieved_context=(
            "A primary key uniquely identifies "
            "each row in a table."
        ),
        expected_keywords=[
            "primary key",
            "unique",
            "database"
        ]
    )

    assert result["relevant"] is True

    assert result["matched_keywords"] == [
        "primary key",
        "unique"
    ]

    assert result["missing_keywords"] == [
        "database"
    ]


def test_empty_context():

    result = evaluate_relevance(
        question="What is PostgreSQL?",
        retrieved_context="",
        expected_keywords=[
            "PostgreSQL"
        ]
    )

    assert result["relevant"] is False

    assert result["matched_keywords"] == []

    assert result["missing_keywords"] == [
        "PostgreSQL"
    ]


def test_empty_question():

    with pytest.raises(ValueError):

        evaluate_relevance(
            question="",
            retrieved_context="Some context",
            expected_keywords=["context"]
        )