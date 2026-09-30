import pytest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from backend.app.agent.graph import handle_final_response
from backend.app.tracing.events import Trace


@pytest.fixture
def mock_save_trace():
    with patch(
        "backend.app.agent.graph.save_trace"
    ) as mock:
        yield mock


def test_valid_final_answer_is_allowed(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content="PostgreSQL is an open-source database."
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "PostgreSQL is an open-source database."
    )

    final_events = [
        event
        for event in trace.events
        if event.event_type == "FINAL_RESPONSE"
    ]

    assert len(final_events) == 1


def test_empty_final_answer_is_rejected(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=""
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "The agent could not generate a valid answer."
    )

    rejected_events = [
        event
        for event in trace.events
        if event.event_type == "FINAL_RESPONSE_REJECTED"
    ]

    assert len(rejected_events) == 1

    assert rejected_events[0].data["reason"] == (
        "invalid_final_answer"
    )


def test_whitespace_final_answer_is_rejected(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content="   "
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "The agent could not generate a valid answer."
    )

    rejected_events = [
        event
        for event in trace.events
        if event.event_type == "FINAL_RESPONSE_REJECTED"
    ]

    assert len(rejected_events) == 1


def test_oversized_final_answer_is_rejected(
    mock_save_trace
):

    trace = Trace()

    oversized_answer = "a" * 5001

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=oversized_answer
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "The agent could not generate a valid answer."
    )

    rejected_events = [
        event
        for event in trace.events
        if event.event_type == "FINAL_RESPONSE_REJECTED"
    ]

    assert len(rejected_events) == 1


def test_final_answer_rejection_is_counted_in_metrics(
    mock_save_trace
):

    trace = Trace()

    handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=""
                )
            ],
            "trace": trace
        }
    )

    metrics = trace.get_metrics()

    assert metrics["final_response_rejections"] == 1


def test_final_answer_with_tool_request_is_rejected(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=(
                        "TOOL_REQUEST: document_search\n"
                        "PostgreSQL is a database."
                    )
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "The agent could not generate a valid answer."
    )

    rejected_events = [
        event
        for event in trace.events
        if event.event_type == "FINAL_RESPONSE_REJECTED"
    ]

    assert len(rejected_events) == 1


def test_final_answer_with_tool_result_is_rejected(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=(
                        "TOOL_RESULT: PostgreSQL supports SQL.\n"
                        "PostgreSQL is a database."
                    )
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "The agent could not generate a valid answer."
    )


def test_final_answer_with_relevance_score_is_rejected(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=(
                        "Relevance Score: 0.91\n"
                        "PostgreSQL is an open-source database."
                    )
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "The agent could not generate a valid answer."
    )


def test_normal_final_answer_is_still_allowed(
    mock_save_trace
):

    trace = Trace()

    result = handle_final_response(
        {
            "messages": [
                AIMessage(
                    content=(
                        "PostgreSQL is an open-source "
                        "object-relational database."
                    )
                )
            ],
            "trace": trace
        }
    )

    assert result["messages"][0].content == (
        "PostgreSQL is an open-source "
        "object-relational database."
    )