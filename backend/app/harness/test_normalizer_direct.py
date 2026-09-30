from langchain_core.messages import AIMessage, HumanMessage

from backend.app.agent.graph import normalize_model_output


content = '{"type":"function","function":{"name":"document_search","parameters":{"query":"foreign key relationship"}}}'

message = AIMessage(
    content=content,
    tool_calls=[]
)

state = {
    "messages": [
        HumanMessage(content="How does a foreign key establish a relationship?"),
        message
    ],
    "tool_call_count": 0,
    "no_relevant_context": False
}

result = normalize_model_output(state)

print("RESULT:", result)

if result:
    normalized_message = result["messages"][0]

    print(
        "TOOL_CALLS:",
        normalized_message.tool_calls
    )

    print(
        "CONTENT:",
        repr(normalized_message.content)
    )
else:
    print("NORMALIZER RETURNED EMPTY RESULT")