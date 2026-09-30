import pytest

from backend.app.harness.validators import (
    validate_user_question,
    validate_final_answer,
    validate_tool_result,
    MAX_QUESTION_LENGTH,
    MAX_ANSWER_LENGTH,
)


def test_valid_user_question():
    assert validate_user_question(
        "What is PostgreSQL?"
    )


def test_empty_user_question_is_rejected():
    assert not validate_user_question("")


def test_whitespace_user_question_is_rejected():
    assert not validate_user_question("   ")


def test_user_question_that_is_too_long_is_rejected():
    question = "a" * (MAX_QUESTION_LENGTH + 1)

    assert not validate_user_question(question)


def test_non_string_question_is_rejected():
    assert not validate_user_question(123)


def test_valid_final_answer():
    assert validate_final_answer(
        "PostgreSQL is a database."
    )


def test_empty_final_answer_is_rejected():
    assert not validate_final_answer("")


def test_final_answer_that_is_too_long_is_rejected():
    answer = "a" * (MAX_ANSWER_LENGTH + 1)

    assert not validate_final_answer(answer)


def test_valid_tool_result():
    assert validate_tool_result(
        "PostgreSQL is a database."
    )


def test_empty_tool_result_is_rejected():
    assert not validate_tool_result("")


def test_none_tool_result_is_rejected():
    assert not validate_tool_result(None)


def test_valid_final_answer():
    assert validate_final_answer(
        "PostgreSQL is an open-source database."
    ) is True


def test_empty_final_answer_is_rejected():
    assert validate_final_answer("") is False


def test_whitespace_final_answer_is_rejected():
    assert validate_final_answer("   ") is False


def test_oversized_final_answer_is_rejected():
    answer = "a" * (MAX_ANSWER_LENGTH + 1)

    assert validate_final_answer(answer) is False


def test_maximum_length_final_answer_is_allowed():
    answer = "a" * MAX_ANSWER_LENGTH

    assert validate_final_answer(answer) is True


def test_non_string_final_answer_is_rejected():
    assert validate_final_answer(None) is False