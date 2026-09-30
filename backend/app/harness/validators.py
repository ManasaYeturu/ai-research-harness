from typing import Any


MAX_QUESTION_LENGTH = 2000
MAX_ANSWER_LENGTH = 5000


# Internal information that should never appear
# in the user-facing final answer.
FORBIDDEN_FINAL_ANSWER_PATTERNS = (
    "TOOL_CALL",
    "TOOL_REQUEST",
    "TOOL_RESULT",
    "TOOL_ERROR",
    "TOOL_REJECTED",
    "FINAL_RESPONSE_REJECTED",
    "Relevance Score:",
    "Chunk ID:",
    "Tool execution failed.",
)


def validate_user_question(
    question: str
) -> bool:
    """
    Validate the user's input before it reaches the agent.
    """

    if not isinstance(question, str):
        return False

    question = question.strip()

    if not question:
        return False

    if len(question) > MAX_QUESTION_LENGTH:
        return False

    return True


def validate_final_answer(
    answer: str
) -> bool:
    """
    Validate the final answer before it is returned
    to the user.
    """

    if not isinstance(answer, str):
        return False

    answer = answer.strip()

    if not answer:
        return False

    if len(answer) > MAX_ANSWER_LENGTH:
        return False

    for pattern in FORBIDDEN_FINAL_ANSWER_PATTERNS:
        if pattern in answer:
            return False

    return True


def validate_tool_result(
    result: Any
) -> bool:
    """
    Validate the result returned by a tool.
    """

    if result is None:
        return False

    if isinstance(result, str):
        return bool(result.strip())

    return True


def normalize_final_answer(
    answer: str
) -> str:
    """
    Remove formatting artifacts produced by the local LLM
    from the final answer.
    """

    if not isinstance(answer, str):
        return answer

    answer = answer.strip()

    if answer.startswith("assistant\n"):
        answer = answer[len("assistant\n"):].lstrip()

    return answer