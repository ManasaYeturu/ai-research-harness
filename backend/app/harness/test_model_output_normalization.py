from langchain_core.messages import AIMessage, HumanMessage

from backend.app.agent.graph import (
    normalize_model_output,
    should_continue
)


def test_normalize_malformed_document_search_call():

    state = {
        "messages": [
            HumanMessage(
                content="How does a foreign key establish a relationship?"
            ),
            AIMessage(
                content=(
                    '{"type":"function",'
                    '"function":{'
                    '"name":"document_search",'
                    '"description":"Search the knowledge base",'
                    '"parameters":{'
                    '"query":"foreign key relationship"'
                    '}}}'
                )
            )
        ],
        "tool_call_count": 0,
        "no_relevant_context": False
    }

    result = normalize_model_output(state)

    message = result["messages"][0]

    assert len(message.tool_calls) == 1

    assert message.tool_calls[0]["name"] == "document_search"

    assert message.tool_calls[0]["args"] == {
        "query": "foreign key relationship"
    }


def test_normalize_does_not_change_normal_assistant_text():

    state = {
        "messages": [
            HumanMessage(
                content="What is a foreign key?"
            ),
            AIMessage(
                content="A foreign key establishes a relationship between tables."
            )
        ],
        "tool_call_count": 0,
        "no_relevant_context": False
    }

    result = normalize_model_output(state)

    assert result == {}


def test_existing_tool_calls_are_not_modified():

    state = {
        "messages": [
            HumanMessage(
                content="What is a foreign key?"
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "document_search",
                        "args": {
                            "query": "foreign key"
                        },
                        "id": "test-tool-call",
                        "type": "tool_call"
                    }
                ]
            )
        ],
        "tool_call_count": 0,
        "no_relevant_context": False
    }

    result = normalize_model_output(state)

    assert result == {}


def test_normalized_call_routes_to_tools():

    state = {
        "messages": [
            HumanMessage(
                content="What is a foreign key?"
            ),
            AIMessage(
                content=(
                    '{"type":"function",'
                    '"function":{'
                    '"name":"document_search",'
                    '"parameters":{'
                    '"query":"foreign key"'
                    '}}}'
                )
            )
        ],
        "tool_call_count": 0,
        "no_relevant_context": False
    }

    normalized = normalize_model_output(state)

    normalized_state = {
        **state,
        **normalized
    }

    assert should_continue(normalized_state) == "tools"