from unittest.mock import patch

from langchain_core.messages import AIMessage

from backend.app.agent.graph import (
    execute_tools_with_policy
)
from backend.app.tracing.events import Trace


def test_invalid_none_tool_result_is_rejected():

    trace = Trace()

    tool_call = {
        "name": "calculator",
        "args": {
            "expression": "10 + 5"
        },
        "id": "test-tool-call-1",
        "type": "tool_call"
    }

    with patch(
        "backend.app.agent.graph.calculator"
    ) as mock_calculator:

        mock_calculator.invoke.return_value = None

        result = execute_tools_with_policy(
            {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            tool_call
                        ]
                    )
                ],
                "tool_call_count": 0,
                "trace": trace
            }
        )

    assert result["tool_call_count"] == 1

    assert len(result["messages"]) == 1

    assert (
        "invalid result"
        in result["messages"][0].content.lower()
    )


def test_empty_string_tool_result_is_rejected():

    trace = Trace()

    tool_call = {
        "name": "calculator",
        "args": {
            "expression": "10 + 5"
        },
        "id": "test-tool-call-2",
        "type": "tool_call"
    }

    with patch(
        "backend.app.agent.graph.calculator"
    ) as mock_calculator:

        mock_calculator.invoke.return_value = ""

        result = execute_tools_with_policy(
            {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            tool_call
                        ]
                    )
                ],
                "tool_call_count": 0,
                "trace": trace
            }
        )

    assert result["tool_call_count"] == 1

    assert len(result["messages"]) == 1

    assert (
        "invalid result"
        in result["messages"][0].content.lower()
    )


def test_valid_tool_result_is_allowed():

    trace = Trace()

    tool_call = {
        "name": "calculator",
        "args": {
            "expression": "10 + 5"
        },
        "id": "test-tool-call-3",
        "type": "tool_call"
    }

    with patch(
        "backend.app.agent.graph.calculator"
    ) as mock_calculator:

        mock_calculator.invoke.return_value = 15

        result = execute_tools_with_policy(
            {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            tool_call
                        ]
                    )
                ],
                "tool_call_count": 0,
                "trace": trace
            }
        )

    assert result["tool_call_count"] == 1

    assert len(result["messages"]) == 1

    assert result["messages"][0].content == "15"