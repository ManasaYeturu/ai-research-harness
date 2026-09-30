from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from backend.app.tracing.events import Trace


class AgentState(TypedDict, total=False):

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

    tool_call_count: int

    no_relevant_context: bool

    retrieved_context: str

    trace: Trace