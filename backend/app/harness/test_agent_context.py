from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage
)

from backend.app.harness.context import limit_context


messages = []


# Add enough messages to force truncation.

for i in range(1, 10):
    messages.append(
        HumanMessage(content=f"Message {i}")
    )


# Add a tool interaction at the boundary.

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


print("Original message count:", len(messages))

controlled_messages = limit_context(messages)

print("Controlled message count:", len(controlled_messages))

print("\nControlled messages:")

for message in controlled_messages:

    if isinstance(message, AIMessage) and message.tool_calls:
        print(
            "AIMessage -> tool call:",
            message.tool_calls
        )

    else:
        print(
            type(message).__name__,
            "->",
            message.content
        )


# --------------------------------------------------
# Validate ToolMessage pairing
# --------------------------------------------------

for index, message in enumerate(controlled_messages):

    if isinstance(message, ToolMessage):

        assert index > 0, (
            "ToolMessage appears without a previous AIMessage"
        )

        previous_message = controlled_messages[index - 1]

        assert isinstance(previous_message, AIMessage), (
            "ToolMessage is not immediately preceded by AIMessage"
        )


# --------------------------------------------------
# Validate AI tool-call pairing
# --------------------------------------------------

for index, message in enumerate(controlled_messages):

    if isinstance(message, AIMessage) and message.tool_calls:

        assert index + 1 < len(controlled_messages), (
            "AIMessage contains a tool call but has no ToolMessage"
        )

        next_message = controlled_messages[index + 1]

        assert isinstance(next_message, ToolMessage), (
            "AI tool call is missing its ToolMessage"
        )


print("\nBoundary tool-pair test PASSED")