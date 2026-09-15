MAX_TOOL_CALLS = 3


def validate_calculator_expression(expression: str) -> bool:
    """
    Validate that a calculator input contains only
    characters allowed in a basic mathematical expression.
    """

    allowed_characters = "0123456789+-*/(). "

    return all(
        character in allowed_characters
        for character in expression
    )


def can_execute_tool(tool_call_count: int) -> bool:
    """
    Check whether the agent is allowed to execute another tool call.
    """

    return tool_call_count < MAX_TOOL_CALLS