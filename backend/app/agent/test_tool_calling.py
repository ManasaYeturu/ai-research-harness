from langchain_ollama import ChatOllama

from backend.app.tools.calculator import calculator


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

llm_with_tools = llm.bind_tools([calculator])


response = llm_with_tools.invoke(
    "What is 125 * 37?"
)

print("CONTENT:")
print(response.content)

print("\nTOOL CALLS:")
print(response.tool_calls)