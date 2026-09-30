<script setup>
import {
    ref,
    watch
} from "vue";

import {
    getRun
} from "../services/api";

const props = defineProps({
    runId: {
        type: String,
        default: null
    }
});

const run = ref(null);
const loading = ref(false);
const error = ref("");

async function loadRun(runId) {
    if (!runId) {
        run.value = null;
        error.value = "";
        return;
    }

    loading.value = true;
    error.value = "";

    try {
        const response =
            await getRun(runId);

        run.value = response;

    } catch (err) {
        run.value = null;

        error.value =
            err.message ||
            "Failed to load run details.";

    } finally {
        loading.value = false;
    }
}

/*
 * Whenever App.vue changes selectedRunId,
 * this watcher loads the corresponding run.
 */
watch(
    () => props.runId,
    (newRunId) => {
        loadRun(newRunId);
    },
    {
        immediate: true
    }
);
</script>

<template>
    <section class="run-details">

        <!-- Header -->
        <div class="run-details-header">

            <div>
                <h2>
                    Run Details
                </h2>

                <p>
                    Execution details for the selected AI run.
                </p>
            </div>

        </div>

        <!-- No run selected -->
        <div
            v-if="!props.runId"
            class="empty-state"
        >
            Select a run to view execution details.
        </div>

        <!-- Loading -->
        <div
            v-else-if="loading"
            class="loading"
        >
            Loading run details...
        </div>

        <!-- Error -->
        <div
            v-else-if="error"
            class="error"
        >
            {{ error }}
        </div>

        <!-- Run -->
        <div
            v-else-if="run"
            class="run-content"
        >

            <!-- Summary -->
            <div class="run-summary">

                <div class="summary-item">
                    <span>
                        Run ID
                    </span>

                    <code>
                        {{ run.run_id }}
                    </code>
                </div>

                <div class="summary-item">
                    <span>
                        Status
                    </span>

                    <strong>
                        {{ run.status }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        Execution Time
                    </span>

                    <strong>
                        {{
                            run.metrics?.execution_time_ms != null
                                ? (
                                    run.metrics.execution_time_ms /
                                    1000
                                ).toFixed(2) + "s"
                                : "N/A"
                        }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        LLM Calls
                    </span>

                    <strong>
                        {{ run.metrics?.llm_calls ?? 0 }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        Tool Calls
                    </span>

                    <strong>
                        {{ run.metrics?.tool_calls ?? 0 }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        Tool Results
                    </span>

                    <strong>
                        {{ run.metrics?.tool_results ?? 0 }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        Tool Rejections
                    </span>

                    <strong>
                        {{ run.metrics?.tool_rejections ?? 0 }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        Tool Errors
                    </span>

                    <strong>
                        {{ run.metrics?.tool_errors ?? 0 }}
                    </strong>
                </div>

                <div class="summary-item">
                    <span>
                        Response Rejections
                    </span>

                    <strong>
                        {{
                            run.metrics
                                ?.final_response_rejections
                            ?? 0
                        }}
                    </strong>
                </div>

            </div>

            <!-- Execution events -->
            <div class="events-section">

                <h3>
                    Execution Events
                </h3>

                <div
                    v-if="
                        !run.events ||
                        run.events.length === 0
                    "
                    class="empty-state"
                >
                    No execution events found.
                </div>

                <div
                    v-else
                    class="events-list"
                >

                    <div
                        v-for="
                            (event, index)
                            in run.events
                        "
                        :key="index"
                        class="event-card"
                    >

                        <div class="event-header">

                            <strong>
                                {{ event.event_type }}
                            </strong>

                            <span>
                                {{ event.timestamp }}
                            </span>

                        </div>

                        <pre>{{
                            JSON.stringify(
                                event.data,
                                null,
                                2
                            )
                        }}</pre>

                    </div>

                </div>

            </div>

            <!-- Sources -->
            <div class="sources-section">

                <h3>
                    Sources
                </h3>

                <div
                    v-if="
                        !run.sources ||
                        run.sources.length === 0
                    "
                    class="empty-state"
                >
                    No sources found.
                </div>

                <div
                    v-else
                    class="sources-list"
                >

                    <div
                        v-for="
                            (source, index)
                            in run.sources
                        "
                        :key="index"
                        class="source-card"
                    >

                        <div class="source-header">

                            <strong>
                                {{ source.source }}
                            </strong>

                            <span>
                                Chunk
                                {{ source.chunk_id }}
                            </span>

                        </div>

                        <div class="source-score">

                            Relevance:

                            {{
                                Number(
                                    source.score
                                ).toFixed(4)
                            }}

                        </div>

                        <div class="source-text">
                            {{ source.text }}
                        </div>

                    </div>

                </div>

            </div>

        </div>

    </section>
</template>

<style scoped>
.run-details {
    width: 100%;
    box-sizing: border-box;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
}

.run-details-header {
    margin-bottom: 20px;
}

.run-details-header h2 {
    margin: 0;
    font-size: 20px;
    color: #111827;
}

.run-details-header p {
    margin: 5px 0 0;
    color: #6b7280;
    font-size: 14px;
}

.empty-state,
.loading {
    padding: 30px;
    text-align: center;
    color: #6b7280;
}

.error {
    padding: 12px;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 8px;
}

/* Summary */

.run-summary {
    display: grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(180px, 1fr)
        );
    gap: 12px;
}

.summary-item {
    padding: 14px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #f9fafb;
}

.summary-item span {
    display: block;
    margin-bottom: 6px;
    color: #6b7280;
    font-size: 12px;
}

.summary-item strong {
    color: #111827;
}

.summary-item code {
    display: block;
    word-break: break-all;
    color: #374151;
    font-size: 11px;
}

/* Events */

.events-section,
.sources-section {
    margin-top: 24px;
}

.events-section h3,
.sources-section h3 {
    margin-bottom: 12px;
    font-size: 16px;
    color: #111827;
}

.events-list,
.sources-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.event-card,
.source-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px;
}

.event-header,
.source-header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
}

.event-header strong,
.source-header strong {
    color: #111827;
}

.event-header span,
.source-header span {
    color: #6b7280;
    font-size: 11px;
}

.event-card pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    background: #f9fafb;
    padding: 12px;
    border-radius: 6px;
    font-size: 11px;
    line-height: 1.5;
}

/* Sources */

.source-score {
    margin-bottom: 8px;
    color: #6b7280;
    font-size: 11px;
}

.source-text {
    padding: 12px;
    background: #f9fafb;
    border-radius: 6px;
    color: #374151;
    font-size: 12px;
    line-height: 1.6;
}

/* Mobile */

@media (max-width: 600px) {
    .run-summary {
        grid-template-columns: 1fr;
    }

    .event-header,
    .source-header {
        align-items: flex-start;
        flex-direction: column;
    }
}
</style>