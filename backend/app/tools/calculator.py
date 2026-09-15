from langchain_core.tools import tool


@tool
def calculator(expression: str) -> float:
    """
    Calculate a basic mathematical expression.

    Use this tool when a user asks for arithmetic calculations.
    """

    allowed_characters = "0123456789+-*/(). "

    if not all(char in allowed_characters for char in expression):
        raise ValueError("Invalid characters in expression")

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return result

    except Exception as e:
        raise ValueError(
            f"Invalid mathematical expression: {expression}"
        ) from e