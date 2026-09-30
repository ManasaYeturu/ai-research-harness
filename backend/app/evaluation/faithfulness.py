from langchain_ollama import ChatOllama


MODEL_NAME = "llama3.2:3b"


faithfulness_llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


FAITHFULNESS_PROMPT = """
You are evaluating whether an AI answer is supported by retrieved context.

Your task is NOT to compare the answer and context as complete sentences.

Instead, evaluate every factual claim made by the ACTUAL ANSWER.

IMPORTANT RULES:

1. Only evaluate claims made by the ACTUAL ANSWER.

2. Do NOT require the answer to contain every fact from the CONTEXT.

3. The answer may contain only a subset of the information in the context.

4. The answer may combine multiple facts from the context into one
   sentence.

5. Different wording and paraphrasing are acceptable.

6. Repeating information from the context is acceptable.

7. Do NOT use outside knowledge.

8. A claim is supported if the context explicitly contains the same
   information, even when the information appears in different parts
   of the context.

Example:

CONTEXT:
PostgreSQL supports tables, primary keys, foreign keys, constraints,
indexes, views, functions, and transactions.

ACTUAL ANSWER:
PostgreSQL supports primary keys and foreign keys.

The context explicitly states that PostgreSQL supports primary keys and
foreign keys.

Therefore:

PASS

Another example:

CONTEXT:
PostgreSQL supports tables, primary keys, foreign keys, constraints,
indexes, views, functions, and transactions.

ACTUAL ANSWER:
PostgreSQL supports primary keys and automatically encrypts all data.

The context supports the primary-key claim but does not support the
encryption claim.

Therefore:

FAIL

Another example:

CONTEXT:
Indexes can improve query performance by allowing PostgreSQL to locate
rows more efficiently.

ACTUAL ANSWER:
Indexes can improve query performance by allowing PostgreSQL to locate
rows more efficiently.

The answer is directly supported by the context.

Therefore:

PASS

Evaluation procedure:

STEP 1:
Identify each factual claim in the ACTUAL ANSWER.

STEP 2:
For each claim, determine whether the CONTEXT explicitly supports it.

STEP 3:
Ignore facts in the CONTEXT that are not mentioned in the ACTUAL ANSWER.

STEP 4:
If every factual claim in the ACTUAL ANSWER is supported, return PASS.

STEP 5:
If at least one important factual claim is not supported, return FAIL.

CONTEXT:
{context}

ACTUAL ANSWER:
{actual_answer}

Return exactly one final decision:

PASS
Reason: <short reason>

or

FAIL
Reason: <short reason>
"""



def _normalize_text(text: str):
    return " ".join(
        text.lower().split()
    )


def _deterministic_check(
    context: str,
    actual_answer: str
):
    normalized_context = _normalize_text(
        context
    )

    normalized_answer = _normalize_text(
        actual_answer
    )

    if not normalized_answer:
        return {
            "passed": False,
            "reason": "The actual answer is empty."
        }

    # Exact answer already exists in the context.
    if normalized_answer in normalized_context:
        return {
            "passed": True,
            "reason": (
                "The actual answer is directly supported by "
                "the retrieved context."
            )
        }

    # Handle simple answers that contain multiple factual terms
    # explicitly present in the context.
    answer_terms = [
        term
        for term in normalized_answer.replace(".", "").split()
        if term
    ]

    important_terms = [
        term
        for term in answer_terms
        if term not in {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "and",
            "or",
            "of",
            "to",
            "in",
            "on",
            "for",
            "with",
            "by",
            "can",
            "be",
            "used",
            "supports"
        }
    ]

    if important_terms and all(
        term in normalized_context
        for term in important_terms
    ):
        return {
            "passed": True,
            "reason": (
                "The factual terms in the answer are explicitly "
                "supported by the retrieved context."
            )
        }

    return None
def evaluate_faithfulness(
    context: str,
    actual_answer: str
):
    deterministic_result = _deterministic_check(
        context,
        actual_answer
    )

    if deterministic_result is not None:
        return deterministic_result

    prompt = FAITHFULNESS_PROMPT.format(
        context=context,
        actual_answer=actual_answer
    )

    response = faithfulness_llm.invoke(
        prompt
    )
    

    result = str(
        response.content
    ).strip()

    lines = [
        line.strip()
        for line in result.splitlines()
        if line.strip()
    ]

    decision = None

    for line in reversed(lines):
        if line == "PASS":
            decision = "PASS"
            break

        if line == "FAIL":
            decision = "FAIL"
            break

    if decision == "PASS":
        passed = True

    elif decision == "FAIL":
        passed = False

    else:
        passed = False

    reason = result

    if "Reason:" in result:
        reason = result.split(
            "Reason:",
            1
        )[1].strip()

    return {
        "passed": passed,
        "reason": reason
    }