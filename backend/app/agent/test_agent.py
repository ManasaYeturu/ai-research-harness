from langchain_core.messages import HumanMessage

from backend.app.agent.graph import build_graph


graph = build_graph()


try:
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is 125 * 37?"
                )
            ],
            "tool_call_count": 0
        }
    )

    print("\nFINAL MESSAGES:\n")

    for message in result["messages"]:
        print(type(message).__name__)
        print(message)
        print("-" * 60)

except Exception as e:
    print("\nAGENT FAILED")
    print(type(e).__name__)
    print(str(e))