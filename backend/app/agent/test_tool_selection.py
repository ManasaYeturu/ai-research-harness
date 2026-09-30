from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

from backend.app.tools.calculator import calculator


from backend.app.agent.graph import (
    build_graph,
    llm_with_tools,
    SYSTEM_PROMPT
)


def test_llm_selects_calculator_for_arithmetic_question():
    llm = ChatOllama(
        model="llama3.2:3b",
        temperature=0
    )

    llm_with_tools = llm.bind_tools(
        [calculator]
    )

    response = llm_with_tools.invoke(
        [
            HumanMessage(
                content="What is 125 * 37?"
            )
        ]
    )

    print("\nModel response:")
    print(response.content)

    print("\nTool calls:")
    print(response.tool_calls)

    assert isinstance(response, AIMessage)

    assert response.tool_calls, (
        "The model did not select the calculator tool."
    )

    calculator_calls = [
        call
        for call in response.tool_calls
        if call["name"] == "calculator"
    ]

    assert calculator_calls, (
        "The model did not select the calculator tool."
    )

    expression = calculator_calls[0]["args"]["expression"]

    assert expression.replace(" ", "") == "125*37"