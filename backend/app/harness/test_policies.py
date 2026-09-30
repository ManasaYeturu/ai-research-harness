from backend.app.harness.policies import is_tool_allowed
from backend.app.harness.policies import (
    is_tool_allowed,
    validate_tool_arguments
)



def test_allowed_tool():
    assert is_tool_allowed("calculator")
    assert is_tool_allowed("document_search")


def test_unknown_tool_is_rejected():
    assert not is_tool_allowed("unknown_tool")


def test_valid_calculator_arguments():
    assert validate_tool_arguments(
        "calculator",
        {"expression": "125 * 37"}
    )


def test_calculator_missing_expression():
    assert not validate_tool_arguments(
        "calculator",
        {}
    )


def test_calculator_invalid_expression():
    assert not validate_tool_arguments(
        "calculator",
        {"expression": "What is PostgreSQL?"}
    )


def test_valid_document_search_arguments():
    assert validate_tool_arguments(
        "document_search",
        {"query": "What is a primary key?"}
    )


def test_document_search_missing_query():
    assert not validate_tool_arguments(
        "document_search",
        {}
    )


def test_document_search_empty_query():
    assert not validate_tool_arguments(
        "document_search",
        {"query": "   "}
    )


def test_unknown_tool_arguments_are_rejected():
    assert not validate_tool_arguments(
        "unknown_tool",
        {}
    )