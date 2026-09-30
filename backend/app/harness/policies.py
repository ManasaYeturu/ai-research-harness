MAX_TOOL_CALLS = 3
ALLOWED_TOOLS = {
    "calculator",
    "document_search",
}


def is_tool_allowed(tool_name: str) -> bool:
    """
    Check whether a tool is allowed to execute
    according to the harness policy.
    """

    return tool_name in ALLOWED_TOOLS



def normalize_tool_arguments(
    tool_name: str,
    tool_args: dict
) -> dict:
    """
    Normalize tool arguments produced by the LLM
    into the canonical argument format expected
    by the harness.
    """

    if not isinstance(tool_args, dict):
        return {}

    # Normal format:
    # {"query": "transactions PostgreSQL"}
    if tool_name == "document_search":
        if "query" in tool_args:
            return {
                "query": tool_args["query"]
            }

        # Handle malformed nested format:
        # {
        #     "type": "function",
        #     "function": "document_search",
        #     "parameters": {
        #         "query": "transactions PostgreSQL"
        #     }
        # }
        parameters = tool_args.get("parameters")

        if isinstance(parameters, dict):
            query = parameters.get("query")

            if isinstance(query, str):
                return {
                    "query": query
                }

    if tool_name == "calculator":
        if "expression" in tool_args:
            return {
                "expression": tool_args["expression"]
            }

        parameters = tool_args.get("parameters")

        if isinstance(parameters, dict):
            expression = parameters.get("expression")

            if isinstance(expression, str):
                return {
                    "expression": expression
                }

    return tool_args



def validate_tool_arguments(
    tool_name: str,
    tool_args: dict
) -> bool:
    """
    Validate the arguments supplied to an allowed tool.
    """

    if not isinstance(tool_args, dict):
        return False

    if tool_name == "calculator":

        expression = tool_args.get("expression")

        if not isinstance(expression, str):
            return False

        if not expression.strip():
            return False

        return validate_calculator_expression(
            expression
        )

    if tool_name == "document_search":

        query = tool_args.get("query")

        if not isinstance(query, str):
            return False

        if not query.strip():
            return False

        return True

    return False


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