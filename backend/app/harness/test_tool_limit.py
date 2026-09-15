from langchain_core.messages import AIMessage

from backend.app.agent.graph import should_continue


def test_execution_limit_stops_agent():

    message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {
                    "expression": "10 * 10"
                },
                "id": "test-tool-call"
            }
        ]
    )

    state = {
        "messages": [message],
        "tool_call_count": 3
    }

    result = should_continue(state)

    print(f"tool_call_count: {state['tool_call_count']}")
    print(f"tool_call_requested: {bool(message.tool_calls)}")
    print(f"graph_decision: {result}")

    assert result == "__end__"

    print("Execution limit test PASSED")


test_execution_limit_stops_agent()