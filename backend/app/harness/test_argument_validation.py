from backend.app.agent.graph import execute_tools_with_policy
from langchain_core.messages import AIMessage


def test_invalid_calculator_arguments_are_rejected_by_agent():

    message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {
                    "expression": "What is PostgreSQL?"
                },
                "id": "test-invalid-calculator",
                "type": "tool_call"
            }
        ]
    )

    result = execute_tools_with_policy(
        {
            "messages": [message],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    tool_message = result["messages"][0]

    assert (
        "Invalid arguments supplied to tool 'calculator'"
        in tool_message.content
    )

    assert result["tool_call_count"] == 0