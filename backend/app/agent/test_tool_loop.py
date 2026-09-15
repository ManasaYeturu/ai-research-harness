from langchain_core.messages import HumanMessage, ToolMessage
from langchain_ollama import ChatOllama

from backend.app.tools.calculator import calculator


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

llm_with_tools = llm.bind_tools([calculator])


messages = [
    HumanMessage(
        content="What is 125 * 37?"
    )
]


print("STEP 1 - Calling LLM")
response = llm_with_tools.invoke(messages)

print("\nAI RESPONSE:")
print(response)

print("\nCONTENT:")
print(response.content)

print("\nTOOL CALLS:")
print(response.tool_calls)

if response.tool_calls:

    tool_call = response.tool_calls[0]

    print("\nSTEP 2 - Executing calculator")

    result = calculator.invoke(
        tool_call["args"]
    )

    print("TOOL RESULT:")
    print(result)

    messages.append(response)

    messages.append(
        ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
    )

    print("\nSTEP 3 - Calling LLM again")

    final_response = llm_with_tools.invoke(messages)

    print("\nFINAL RESPONSE:")
    print(final_response)

else:
    print("\nNO STRUCTURED TOOL CALL FOUND")