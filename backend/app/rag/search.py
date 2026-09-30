import re

from langchain_ollama import OllamaEmbeddings

from backend.app.rag.vector_store import (
    client,
    COLLECTION_NAME
)


EMBEDDING_MODEL = "nomic-embed-text"

DEFAULT_TOP_K = 3
DEFAULT_SCORE_THRESHOLD = 0.5


STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "does",
    "do",
    "how",
    "why",
    "when",
    "where",
    "which",
    "who",
    "can",
    "could",
    "should",
    "in",
    "on",
    "of",
    "to",
    "for",
    "with",
    "and",
    "or",
    "about",
    "used",
    "use",
}


embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL
)


def normalize_term(term: str) -> str:
    """
    Normalize simple singular/plural variations.

    Examples:
        supports -> support
        indexes -> index
        transactions -> transaction
        queries -> query
    """

    term = term.lower().strip()

    if len(term) <= 3:
        return term

    if term.endswith("ies"):
        return term[:-3] + "y"

    if term.endswith("es"):
        return term[:-2]

    if term.endswith("s"):
        return term[:-1]

    return term


def extract_keywords(text: str) -> set[str]:
    """
    Extract meaningful keywords from text.

    This function is kept as a simple lexical helper.
    It removes common stop words but does not perform
    singular/plural normalization.
    """

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    }


def extract_terms(text: str) -> set[str]:
    """
    Extract meaningful normalized terms from text.

    Stop words are removed and simple singular/plural
    variations are normalized.
    """

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return {
        normalize_term(word)
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    }


def has_lexical_relevance(
    query: str,
    content: str
) -> bool:
    """
    Check whether the query and content have at least
    one meaningful normalized term in common.

    This helper is retained for compatibility with the
    existing RAG tests.
    """

    query_terms = extract_terms(query)
    content_terms = extract_terms(content)

    if not query_terms:
        return True

    overlap = query_terms.intersection(
        content_terms
    )

    return len(overlap) > 0


def calculate_term_coverage(
    query: str,
    text: str
) -> tuple[float, list[str]]:
    """
    Calculate how much of the meaningful query vocabulary
    appears in the retrieved text.

    Returns:

        coverage:
            Value between 0.0 and 1.0.

        matched_terms:
            Query terms found in the text.
    """

    query_terms = extract_terms(query)
    text_terms = extract_terms(text)

    if not query_terms:
        return 0.0, []

    matched_terms = [
        term
        for term in query_terms
        if term in text_terms
    ]

    coverage = (
        len(matched_terms)
        / len(query_terms)
    )

    return coverage, matched_terms


def is_content_relevant(
    query: str,
    text: str
) -> bool:
    """
    Determine whether retrieved content has sufficient
    lexical overlap with the user's query.

    At least 50% of the meaningful query terms must
    appear in the retrieved content.
    """

    coverage, matched_terms = (
        calculate_term_coverage(
            query,
            text
        )
    )

    if not matched_terms:
        return False

    return coverage >= 0.5


def search_similar_chunks(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    source_filter: str | None = None
):
    """
    Search Qdrant for semantically similar chunks.

    Retrieval pipeline:

    1. Validate the query and search parameters.
    2. Generate the query embedding.
    3. Retrieve semantic candidates from Qdrant.
    4. Apply the similarity score threshold.
    5. Apply content relevance filtering.
    6. Apply the optional source filter.
    7. Remove duplicate chunks.
    8. Return the final top-k results.
    """

    # --------------------------------------------------
    # 1. Validate input
    # --------------------------------------------------

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty"
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0"
        )

    if not 0 <= score_threshold <= 1:
        raise ValueError(
            "score_threshold must be between 0 and 1"
        )

    if (
        source_filter is not None
        and not source_filter.strip()
    ):
        raise ValueError(
            "source_filter cannot be empty"
        )

    # --------------------------------------------------
    # 2. Convert query into an embedding
    # --------------------------------------------------

    query_vector = embeddings.embed_query(
        query
    )

    # --------------------------------------------------
    # 3. Retrieve more candidates than final top_k
    # --------------------------------------------------

    candidate_limit = max(
        top_k * 3,
        top_k
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=candidate_limit,
        with_payload=True
    )

    # --------------------------------------------------
    # 4. Process retrieved candidates
    # --------------------------------------------------

    matches = []

    seen_chunks = set()

    for result in results.points:

        # ----------------------------------------------
        # 4.1 Semantic similarity threshold
        # ----------------------------------------------

        if result.score < score_threshold:
            continue

        # ----------------------------------------------
        # 4.2 Read payload
        # ----------------------------------------------

        payload = result.payload or {}

        text = payload.get(
            "text",
            ""
        )

        source = payload.get(
            "source"
        )

        chunk_id = payload.get(
            "chunk_id"
        )

        # Ignore malformed chunks.
        if not text:
            continue

        # ----------------------------------------------
        # 4.3 Optional source filter
        # ----------------------------------------------

        if source_filter is not None:

            if source != source_filter:
                continue

        # ----------------------------------------------
        # 4.4 Content relevance filtering
        # ----------------------------------------------

        if not is_content_relevant(
            query,
            text
        ):
            continue

        # ----------------------------------------------
        # 4.5 Duplicate prevention
        # ----------------------------------------------

        chunk_key = (
            source,
            chunk_id
        )

        if chunk_key in seen_chunks:
            continue

        seen_chunks.add(chunk_key)

        # ----------------------------------------------
        # 4.6 Store accepted result
        # ----------------------------------------------

        matches.append(
            {
                "score": result.score,
                "source": source,
                "chunk_id": chunk_id,
                "text": text
            }
        )

    # --------------------------------------------------
    # 5. Return strongest final results
    # --------------------------------------------------

    return matches[:top_k]