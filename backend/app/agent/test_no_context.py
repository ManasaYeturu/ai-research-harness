from langchain_core.messages import HumanMessage

from backend.app.agent.graph import build_graph


def test_agent_does_not_hallucinate_when_no_context_is_found():
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is the capital of France?"
                )
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    final_message = result["messages"][-1]

    assert (
        final_message.content
        == "I couldn't find relevant information in the knowledge base to answer that question."
    )

    assert "Paris" not in final_message.content