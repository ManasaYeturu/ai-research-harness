from langchain_core.messages import AIMessage

from backend.app.agent.graph import build_graph


def test_unknown_tool_is_rejected_by_agent():
    graph = build_graph()

    fake_tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "unknown_tool",
                "args": {},
                "id": "test-tool-call-1",
                "type": "tool_call"
            }
        ]
    )

    result = graph.nodes["tools"].invoke(
        {
            "messages": [fake_tool_call],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    tool_message = result["messages"][0]

    assert "not allowed" in tool_message.content