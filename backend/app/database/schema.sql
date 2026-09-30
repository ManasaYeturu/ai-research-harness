CREATE TABLE IF NOT EXISTS runs (
    run_id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS trace_events (
    event_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_trace_events_run
        FOREIGN KEY (run_id)
        REFERENCES runs(run_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_trace_events_run_id
    ON trace_events(run_id);

CREATE INDEX IF NOT EXISTS idx_trace_events_timestamp
    ON trace_events(timestamp);