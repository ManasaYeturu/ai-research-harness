from langchain_core.messages import AIMessage, ToolMessage


MAX_CONTEXT_MESSAGES = 10


def _has_tool_call(message):
    """
    Check whether an AIMessage contains one or more tool calls.
    """

    return (
        isinstance(message, AIMessage)
        and bool(message.tool_calls)
    )


def _is_valid_tool_pair(messages, index):
    """
    Validate that an AI tool call is immediately followed
    by its corresponding ToolMessage.
    """

    message = messages[index]

    if not _has_tool_call(message):
        return True

    if index + 1 >= len(messages):
        return False

    next_message = messages[index + 1]

    if not isinstance(next_message, ToolMessage):
        return False

    tool_call_ids = {
        tool_call.get("id")
        for tool_call in message.tool_calls
        if isinstance(tool_call, dict)
    }

    if not tool_call_ids:
        return False

    return next_message.tool_call_id in tool_call_ids
def _remove_incomplete_tool_pairs(messages):
    """
    Remove messages that would create incomplete tool
    interactions after context truncation.
    """

    if not messages:
        return messages

    cleaned_messages = list(messages)

    changed = True

    while changed:

        changed = False

        # Remove an orphan ToolMessage.

        for index, message in enumerate(cleaned_messages):

            if isinstance(message, ToolMessage):

                if index == 0:
                    cleaned_messages.pop(index)
                    changed = True
                    break

                previous_message = cleaned_messages[index - 1]

                if not isinstance(previous_message, AIMessage):
                    cleaned_messages.pop(index)
                    changed = True
                    break

        if changed:
            continue

        # Remove an AI tool call without its ToolMessage.

        for index, message in enumerate(cleaned_messages):

            if _has_tool_call(message):

                if not _is_valid_tool_pair(
                    cleaned_messages,
                    index
                ):
                    cleaned_messages.pop(index)
                    changed = True
                    break

    return cleaned_messages


def limit_context(messages):
    """
    Limit the number of messages passed to the LLM
    while preserving valid tool-call relationships.
    """

    if len(messages) > MAX_CONTEXT_MESSAGES:
        controlled_messages = messages[-MAX_CONTEXT_MESSAGES:]
    else:
        controlled_messages = list(messages)

    controlled_messages = _remove_incomplete_tool_pairs(
        controlled_messages
    )

    return controlled_messages