from .events import Trace


class Tracer:

    def __init__(self):
        self.traces: dict[str, Trace] = {}

    def start_trace(self) -> Trace:

        trace = Trace()

        self.traces[trace.run_id] = trace

        return trace

    def get_trace(self, run_id: str) -> Trace | None:

        return self.traces.get(run_id)