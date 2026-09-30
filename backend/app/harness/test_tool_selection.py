from langchain_core.messages import (
    AIMessage,
    HumanMessage
)

from backend.app.agent.graph import build_graph


def test_agent_selects_document_search_for_knowledge_question():
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

    messages = result["messages"]

    tool_calls = [
        call
        for message in messages
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    ]

    document_search_calls = [
        call
        for call in tool_calls
        if call["name"] == "document_search"
    ]

    assert document_search_calls


def test_agent_selects_calculator_for_arithmetic_question():
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is 125 * 37?"
                )
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    messages = result["messages"]

    tool_calls = [
        call
        for message in messages
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    ]

    calculator_calls = [
        call
        for call in tool_calls
        if call["name"] == "calculator"
    ]

    assert calculator_calls

    expression = calculator_calls[0]["args"]["expression"]

    assert expression.replace(" ", "") == "125*37"