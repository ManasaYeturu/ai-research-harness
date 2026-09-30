from langchain_core.messages import HumanMessage

from backend.app.agent.graph import build_graph


def test_basic_agent():
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is PostgreSQL?"
                )
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    assert result["messages"]