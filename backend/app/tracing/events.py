from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class TraceEvent:
    event_type: str

    data: dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class Trace:
    run_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed_at: datetime | None = None

    events: list[TraceEvent] = field(
        default_factory=list
    )

    status: str = "running"

    def add_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None
    ):
        event = TraceEvent(
            event_type=event_type,
            data=data or {}
        )

        self.events.append(event)

        return event

    def complete(self):
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def fail(self):
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)

    def get_metrics(self):
        llm_calls = 0
        tool_calls = 0
        tool_rejections = 0
        tool_results = 0
        tool_errors = 0
        final_response_rejections = 0

        for event in self.events:

            if event.event_type == "LLM_REQUEST":
                llm_calls += 1

            elif event.event_type == "TOOL_REQUEST":
                tool_calls += 1

            elif event.event_type == "TOOL_REJECTED":
                tool_rejections += 1

            elif event.event_type == "TOOL_RESULT":
                tool_results += 1

            elif event.event_type == "TOOL_ERROR":
                tool_errors += 1

            elif event.event_type == "FINAL_RESPONSE_REJECTED":
                final_response_rejections += 1

        execution_time_ms = None

        if self.completed_at:
            execution_time_ms = (
                self.completed_at - self.started_at
            ).total_seconds() * 1000

        return {
            "execution_time_ms": execution_time_ms,
            "llm_calls": llm_calls,
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "tool_rejections": tool_rejections,
            "tool_errors": tool_errors,
            "final_response_rejections": final_response_rejections,
        }