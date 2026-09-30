import pytest

from backend.app.rag.search import (
    search_similar_chunks,
    calculate_term_coverage,
    is_content_relevant,
)


def test_relevant_postgresql_query_returns_results():
    results = search_similar_chunks(
        "What does PostgreSQL support?"
    )

    assert results
    assert any(
        result["source"] == "postgres.md"
        for result in results
    )


def test_transaction_query_returns_relevant_results():
    results = search_similar_chunks(
        "What does PostgreSQL say about transactions?"
    )

    assert results

    combined_text = " ".join(
        result["text"]
        for result in results
    ).lower()

    assert "transactions" in combined_text


def test_irrelevant_quantum_query_returns_no_results():
    results = search_similar_chunks(
        "What does PostgreSQL say about quantum computing?"
    )

    assert results == []


def test_support_matches_supports():
    coverage, matched_terms = (
        calculate_term_coverage(
            "What does PostgreSQL support?",
            "PostgreSQL supports tables and indexes."
        )
    )

    assert coverage == 1.0
    assert "support" in matched_terms


def test_transactions_matches_transaction():
    assert is_content_relevant(
        "transactions",
        "Transactions allow multiple database operations."
    )


def test_empty_query_is_rejected():
    with pytest.raises(ValueError):
        search_similar_chunks("")


def test_invalid_top_k_is_rejected():
    with pytest.raises(ValueError):
        search_similar_chunks(
            "What is PostgreSQL?",
            top_k=0
        )


def test_invalid_score_threshold_is_rejected():
    with pytest.raises(ValueError):
        search_similar_chunks(
            "What is PostgreSQL?",
            score_threshold=1.5
        )


def test_source_filter_returns_matching_source():
    results = search_similar_chunks(
        "What is PostgreSQL?",
        source_filter="postgres.md"
    )

    assert results

    assert all(
        result["source"] == "postgres.md"
        for result in results
    )


def test_source_filter_returns_no_results_for_unknown_source():
    results = search_similar_chunks(
        "What is PostgreSQL?",
        source_filter="unknown.md"
    )

    assert results == []


def test_invalid_empty_source_filter_is_rejected():
    with pytest.raises(ValueError):
        search_similar_chunks(
            "What is PostgreSQL?",
            source_filter="   "
        )


def test_top_k_limits_final_results():
    results = search_similar_chunks(
        "What does PostgreSQL support?",
        top_k=1
    )

    assert len(results) <= 1


def test_extract_keywords_removes_stop_words():
    from backend.app.rag.search import extract_keywords

    keywords = extract_keywords(
        "What is a primary key?"
    )

    assert "what" not in keywords
    assert "is" not in keywords
    assert "primary" in keywords
    assert "key" in keywords

def test_lexical_relevance_detects_matching_content():
    from backend.app.rag.search import has_lexical_relevance

    assert has_lexical_relevance(
        "What is a primary key?",
        "A primary key uniquely identifies each row in a table."
    )

def test_lexical_relevance_rejects_unrelated_content():
    from backend.app.rag.search import has_lexical_relevance

    assert not has_lexical_relevance(
        "What is quantum computing?",
        "PostgreSQL is an open-source object-relational database."
    )