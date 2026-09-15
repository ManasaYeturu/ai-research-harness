from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from backend.app.tools.calculator import calculator


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

llm_with_tools = llm.bind_tools([calculator])


questions = [
    "What is 125 * 37?",
    "What is PostgreSQL?"
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)

    response = llm_with_tools.invoke(
        [
            HumanMessage(content=question)
        ]
    )

    print("\nCONTENT:")
    print(response.content)

    print("\nTOOL CALLS:")
    print(response.tool_calls)