from backend.app.harness.policies import (
    is_tool_allowed,
    validate_tool_arguments,
    can_execute_tool,
    MAX_TOOL_CALLS
)


def test_calculator_valid_arguments_are_allowed():

    tool_name = "calculator"

    tool_args = {
        "expression": "125 * 37"
    }

    assert is_tool_allowed(tool_name)

    assert validate_tool_arguments(
        tool_name,
        tool_args
    )


def test_calculator_invalid_arguments_are_rejected():

    tool_name = "calculator"

    tool_args = {
        "expression": "__import__('os').system('dir')"
    }

    assert is_tool_allowed(tool_name)

    assert not validate_tool_arguments(
        tool_name,
        tool_args
    )


def test_unknown_tool_is_rejected():

    tool_name = "delete_database"

    tool_args = {}

    assert not is_tool_allowed(tool_name)

    assert not validate_tool_arguments(
        tool_name,
        tool_args
    )


def test_tool_execution_limit_is_enforced():

    assert can_execute_tool(
        MAX_TOOL_CALLS - 1
    )

    assert not can_execute_tool(
        MAX_TOOL_CALLS
    )