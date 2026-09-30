from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage
)

from backend.app.harness.context import limit_context


def test_context_unchanged_when_within_limit():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 6)
    ]

    result = limit_context(messages)

    assert result == messages


def test_context_unchanged_at_limit():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 11)
    ]

    result = limit_context(messages)

    assert result == messages


def test_context_keeps_latest_messages_when_over_limit():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 16)
    ]

    result = limit_context(messages)

    assert len(result) == 10
    assert result == messages[-10:]


def test_context_preserves_valid_tool_pair():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 10)
    ]

    messages.append(
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculator",
                    "args": {"expression": "10 * 10"},
                    "id": "tool-call-1",
                    "type": "tool_call"
                }
            ]
        )
    )

    messages.append(
        ToolMessage(
            content="100",
            tool_call_id="tool-call-1"
        )
    )

    result = limit_context(messages)

    assert len(result) == 10

    tool_call_messages = [
        message
        for message in result
        if isinstance(message, AIMessage)
        and message.tool_calls
    ]

    tool_result_messages = [
        message
        for message in result
        if isinstance(message, ToolMessage)
    ]

    assert len(tool_call_messages) == 1
    assert len(tool_result_messages) == 1

    assert (
        tool_call_messages[0].tool_calls[0]["id"]
        == tool_result_messages[0].tool_call_id
    )


def test_context_removes_mismatched_tool_pair():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 10)
    ]

    messages.append(
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculator",
                    "args": {"expression": "10 * 10"},
                    "id": "tool-call-1",
                    "type": "tool_call"
                }
            ]
        )
    )

    messages.append(
        ToolMessage(
            content="100",
            tool_call_id="wrong-tool-call-id"
        )
    )

    result = limit_context(messages)

    tool_call_messages = [
        message
        for message in result
        if isinstance(message, AIMessage)
        and message.tool_calls
    ]

    tool_result_messages = [
        message
        for message in result
        if isinstance(message, ToolMessage)
    ]

    assert tool_call_messages == []
    assert tool_result_messages == []


def test_context_removes_orphan_tool_message():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 10)
    ]

    messages.append(
        ToolMessage(
            content="100",
            tool_call_id="tool-call-1"
        )
    )

    result = limit_context(messages)

    tool_messages = [
        message
        for message in result
        if isinstance(message, ToolMessage)
    ]

    assert tool_messages == []


def test_context_removes_unfinished_tool_call():
    messages = [
        HumanMessage(content=f"Message {i}")
        for i in range(1, 10)
    ]

    messages.append(
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculator",
                    "args": {"expression": "10 * 10"},
                    "id": "tool-call-1",
                    "type": "tool_call"
                }
            ]
        )
    )

    result = limit_context(messages)

    tool_call_messages = [
        message
        for message in result
        if isinstance(message, AIMessage)
        and message.tool_calls
    ]

    assert tool_call_messages == []