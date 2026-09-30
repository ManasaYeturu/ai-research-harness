from backend.app.evaluation.retrieval import (
    evaluate_retrieval
)


def test_expected_source_was_retrieved():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "Source: postgres.md\n"
            "Chunk ID: 1\n"
            "Content:\n"
            "A primary key uniquely identifies each row."
        )
    )

    assert result["passed"] is True


def test_expected_source_was_not_retrieved():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "Source: python.md\n"
            "Chunk ID: 1\n"
            "Content:\n"
            "Python is a programming language."
        )
    )

    assert result["passed"] is False


def test_expected_source_but_no_context():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "No relevant information was found."
        )
    )

    assert result["passed"] is False


def test_no_source_expected_and_no_context():

    result = evaluate_retrieval(
        expected_source=None,
        retrieved_context=(
            "No relevant information was found."
        )
    )

    assert result["passed"] is True


def test_no_source_expected_but_context_returned():

    result = evaluate_retrieval(
        expected_source=None,
        retrieved_context=(
            "Source: postgres.md\n"
            "Chunk ID: 1\n"
            "Content:\n"
            "PostgreSQL is a database."
        )
    )

    assert result["passed"] is False


def test_empty_context_when_no_source_expected():

    result = evaluate_retrieval(
        expected_source=None,
        retrieved_context=""
    )

    assert result["passed"] is True


def test_retrieved_content_contains_expected_keywords():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "Source: postgres.md\n"
            "Chunk ID: 1\n"
            "Content:\n"
            "A primary key uniquely identifies each row in a table."
        ),
        expected_keywords=[
            "primary key",
            "uniquely",
            "identifies",
            "row",
            "table"
        ]
    )

    assert result["passed"] is True


def test_retrieved_content_does_not_contain_expected_keywords():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "Source: postgres.md\n"
            "Chunk ID: 2\n"
            "Content:\n"
            "PostgreSQL is commonly used for web applications."
        ),
        expected_keywords=[
            "primary key",
            "uniquely",
            "identifies",
            "row",
            "table"
        ]
    )

    assert result["passed"] is False


def test_retrieval_result_contains_source_information():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "Source: postgres.md\n"
            "Chunk ID: 1\n"
            "Content:\n"
            "A primary key uniquely identifies each row."
        ),
        expected_keywords=[
            "primary key",
            "uniquely"
        ]
    )

    assert result["passed"] is True
    assert result["expected_source"] == "postgres.md"
    assert result["source_found"] is True
    assert result["missing_keywords"] == []
    assert result["content_relevant"] is True


def test_retrieval_result_reports_missing_keywords():

    result = evaluate_retrieval(
        expected_source="postgres.md",
        retrieved_context=(
            "Source: postgres.md\n"
            "Chunk ID: 2\n"
            "Content:\n"
            "PostgreSQL is commonly used for web applications."
        ),
        expected_keywords=[
            "primary key",
            "uniquely",
            "identifies"
        ]
    )

    assert result["passed"] is False
    assert result["expected_source"] == "postgres.md"
    assert result["source_found"] is True
    assert result["content_relevant"] is False

    assert result["missing_keywords"] == [
        "primary key",
        "uniquely",
        "identifies"
    ]