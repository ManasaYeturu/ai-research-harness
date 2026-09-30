def evaluate_relevance(
    question: str,
    retrieved_context: str,
    expected_keywords: list[str] | None = None
):
    """
    Evaluate whether retrieved context is relevant to the question.

    This first version uses expected keywords as a deterministic
    evaluation signal.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if not retrieved_context or not retrieved_context.strip():
        return {
            "relevant": False,
            "matched_keywords": [],
            "missing_keywords": (
                expected_keywords or []
            ),
            "reason": "No retrieved context was provided."
        }

    if not expected_keywords:
        return {
            "relevant": True,
            "matched_keywords": [],
            "missing_keywords": [],
            "reason": (
                "No expected keywords were provided, "
                "so relevance could not be evaluated "
                "using keyword matching."
            )
        }

    normalized_context = retrieved_context.lower()

    matched_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:

        if keyword.lower() in normalized_context:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    relevant = len(matched_keywords) > 0

    return {
        "relevant": relevant,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "reason": (
            "Retrieved context contains relevant "
            "expected information."
            if relevant
            else
            "Retrieved context does not contain "
            "the expected information."
        )
    }