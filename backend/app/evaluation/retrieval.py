def evaluate_retrieval(
    expected_source: str | None,
    retrieved_context: str,
    expected_keywords: list[str] | None = None
):
    """
    Evaluate retrieval source and content relevance.
    """

    no_result_message = (
        "No relevant information was found."
    )

    missing_keywords = []

    source_found = False

    content_relevant = True

    # --------------------------------------------------
    # Case 1:
    # No source is expected.
    # --------------------------------------------------

    if expected_source is None:

        if (
            not retrieved_context
            or retrieved_context.strip()
            == no_result_message
        ):
            return {
                "passed": True,
                "expected_source": None,
                "source_found": False,
                "missing_keywords": [],
                "content_relevant": True,
                "reason": (
                    "No relevant source was expected and "
                    "no relevant context was retrieved."
                )
            }

        return {
            "passed": False,
            "expected_source": None,
            "source_found": False,
            "missing_keywords": [],
            "content_relevant": False,
            "reason": (
                "No relevant source was expected, but "
                "retrieved context was returned."
            )
        }

    # --------------------------------------------------
    # Case 2:
    # A source is expected, but nothing was retrieved.
    # --------------------------------------------------

    if (
        not retrieved_context
        or retrieved_context.strip()
        == no_result_message
    ):
        return {
            "passed": False,
            "expected_source": expected_source,
            "source_found": False,
            "missing_keywords": (
                expected_keywords or []
            ),
            "content_relevant": False,
            "reason": (
                f"Expected source '{expected_source}', "
                "but no relevant context was retrieved."
            )
        }

    # --------------------------------------------------
    # Case 3:
    # Check expected source.
    # --------------------------------------------------

    source_marker = f"Source: {expected_source}"

    if source_marker in retrieved_context:
        source_found = True

    else:
        return {
            "passed": False,
            "expected_source": expected_source,
            "source_found": False,
            "missing_keywords": (
                expected_keywords or []
            ),
            "content_relevant": False,
            "reason": (
                f"Expected source '{expected_source}' "
                "was not found in the retrieved context."
            )
        }

    # --------------------------------------------------
    # Case 4:
    # Check expected keywords.
    # --------------------------------------------------

    if expected_keywords:

        normalized_context = retrieved_context.lower()

        for keyword in expected_keywords:

            if keyword.lower() not in normalized_context:
                missing_keywords.append(keyword)

        if missing_keywords:
            content_relevant = False

    # --------------------------------------------------
    # Case 5:
    # Final result.
    # --------------------------------------------------

    if not content_relevant:

        return {
            "passed": False,
            "expected_source": expected_source,
            "source_found": source_found,
            "missing_keywords": missing_keywords,
            "content_relevant": False,
            "reason": (
                "Expected source was retrieved, but "
                "the retrieved content does not contain "
                f"the expected keywords: {missing_keywords}"
            )
        }

    return {
        "passed": True,
        "expected_source": expected_source,
        "source_found": source_found,
        "missing_keywords": [],
        "content_relevant": True,
        "reason": (
            f"Expected source '{expected_source}' "
            "was retrieved and the retrieved content "
            "contains the expected information."
        )
    }