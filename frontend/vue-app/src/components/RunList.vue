<script setup>
import { onMounted, ref } from "vue";

import {
    getRuns,
    getRunsSummary
} from "../services/api";

const runs = ref([]);

const summary = ref({
    total_runs: 0,
    completed_runs: 0,
    failed_runs: 0,
    running_runs: 0,
    completion_rate: 0,
    average_execution_time_ms: 0,
    llm_calls: 0,
    average_llm_calls_per_run: 0,
    tool_calls: 0,
    tool_rejections: 0,
    tool_rejection_rate: 0
});

const loading = ref(true);
const error = ref("");
const selectedRunId = ref(null);

const selectedStatus = ref("all");

const emit = defineEmits(["select-run"]);


/* =========================
   Load Dashboard
========================= */

async function loadDashboard() {
    loading.value = true;
    error.value = "";

    try {
        const status =
            selectedStatus.value === "all"
                ? null
                : selectedStatus.value;

        const [
            runsResponse,
            summaryResponse
        ] = await Promise.all([
            getRuns(status),
            getRunsSummary()
        ]);

        runs.value = runsResponse.runs;
        summary.value = summaryResponse;

    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
}


/* =========================
   Status Filter
========================= */

function changeStatus(status) {
    selectedStatus.value = status;
    selectedRunId.value = null;

    loadDashboard();
}


/* =========================
   Select Run
========================= */

function selectRun(runId) {
    selectedRunId.value = runId;

    emit(
        "select-run",
        runId
    );
}


/* =========================
   Formatting
========================= */

function formatDate(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(
        dateValue
    ).toLocaleString();
}


function formatDuration(run) {
    if (
        !run.started_at ||
        !run.completed_at
    ) {
        return "-";
    }

    const start = new Date(
        run.started_at
    );

    const end = new Date(
        run.completed_at
    );

    const milliseconds =
        end - start;

    if (milliseconds < 1000) {
        return `${milliseconds} ms`;
    }

    return `${(
        milliseconds / 1000
    ).toFixed(2)} s`;
}


function formatAverageDuration(
    milliseconds
) {
    if (
        milliseconds === null ||
        milliseconds === undefined
    ) {
        return "-";
    }

    if (milliseconds < 1000) {
        return `${milliseconds.toFixed(0)} ms`;
    }

    return `${(
        milliseconds / 1000
    ).toFixed(2)} s`;
}


function formatPercentage(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "-";
    }

    return `${value.toFixed(2)}%`;
}


function getStatusClass(status) {
    return `status-${status}`;
}


/* =========================
   Initial Load
========================= */

onMounted(() => {
    loadDashboard();
});
</script>


<template>

    <section class="run-list">

        <!-- =========================
             Header
        ========================== -->

        <div class="section-header">

            <div>

                <h2>
                    Runs
                </h2>

                <p>
                    Recent AI agent executions
                </p>

            </div>


            <button
                class="refresh-button"
                @click="loadDashboard"
                :disabled="loading"
            >
                {{
                    loading
                        ? "Loading..."
                        : "Refresh"
                }}
            </button>

        </div>


        <!-- =========================
             Status Filters
        ========================== -->

        <div class="status-filters">

            <button
                class="filter-button"
                :class="{
                    active:
                        selectedStatus === 'all'
                }"
                @click="
                    changeStatus('all')
                "
            >
                All
            </button>


            <button
                class="filter-button"
                :class="{
                    active:
                        selectedStatus ===
                        'completed'
                }"
                @click="
                    changeStatus('completed')
                "
            >
                Completed
            </button>


            <button
                class="filter-button"
                :class="{
                    active:
                        selectedStatus ===
                        'running'
                }"
                @click="
                    changeStatus('running')
                "
            >
                Running
            </button>


            <button
                class="filter-button"
                :class="{
                    active:
                        selectedStatus ===
                        'failed'
                }"
                @click="
                    changeStatus('failed')
                "
            >
                Failed
            </button>

        </div>


        <!-- =========================
             Summary Cards
        ========================== -->

        <div class="summary-grid">

            <div class="summary-card">

                <span class="summary-label">
                    Total Runs
                </span>

                <strong>
                    {{ summary.total_runs }}
                </strong>

            </div>


            <div
                class="summary-card completed-card"
            >

                <span class="summary-label">
                    Completed
                </span>

                <strong>
                    {{ summary.completed_runs }}
                </strong>

            </div>


            <div
                class="summary-card failed-card"
            >

                <span class="summary-label">
                    Failed
                </span>

                <strong>
                    {{ summary.failed_runs }}
                </strong>

            </div>


            <div
                class="summary-card running-card"
            >

                <span class="summary-label">
                    Running
                </span>

                <strong>
                    {{ summary.running_runs }}
                </strong>

            </div>

        </div>


        <!-- =========================
             Observability Metrics
        ========================== -->

        <div class="observability-grid">

            <div class="observability-card">

                <span>
                    Completion Rate
                </span>

                <strong>
                    {{
                        formatPercentage(
                            summary.completion_rate
                        )
                    }}
                </strong>

            </div>


            <div class="observability-card">

                <span>
                    Avg Execution Time
                </span>

                <strong>
                    {{
                        formatAverageDuration(
                            summary.average_execution_time_ms
                        )
                    }}
                </strong>

            </div>


            <div class="observability-card">

                <span>
                    LLM Calls
                </span>

                <strong>
                    {{ summary.llm_calls }}
                </strong>

            </div>


            <div class="observability-card">

                <span>
                    Avg LLM Calls / Run
                </span>

                <strong>
                    {{
                        summary.average_llm_calls_per_run.toFixed(
                            2
                        )
                    }}
                </strong>

            </div>


            <div class="observability-card">

                <span>
                    Tool Calls
                </span>

                <strong>
                    {{ summary.tool_calls }}
                </strong>

            </div>


            <div class="observability-card">

                <span>
                    Tool Rejections
                </span>

                <strong>
                    {{ summary.tool_rejections }}
                </strong>

            </div>


            <div class="observability-card">

                <span>
                    Tool Rejection Rate
                </span>

                <strong>
                    {{
                        formatPercentage(
                            summary.tool_rejection_rate
                        )
                    }}
                </strong>

            </div>

        </div>


        <!-- =========================
             Loading State
        ========================== -->

        <div
            v-if="loading"
            class="state-message"
        >
            Loading runs...
        </div>


        <!-- =========================
             Error State
        ========================== -->

        <div
            v-else-if="error"
            class="state-message error"
        >
            {{ error }}
        </div>


        <!-- =========================
             Empty State
        ========================== -->

        <div
            v-else-if="runs.length === 0"
            class="state-message"
        >
            No runs found.
        </div>


        <!-- =========================
             Runs Table
        ========================== -->

        <div
            v-else
            class="runs-table"
        >

            <div class="table-header">

                <span>
                    Run ID
                </span>

                <span>
                    Status
                </span>

                <span>
                    Started
                </span>

                <span>
                    Completed
                </span>

                <span>
                    Duration
                </span>

            </div>


            <button
                v-for="run in runs"
                :key="run.run_id"
                class="run-row"
                :class="{
                    selected:
                        selectedRunId ===
                        run.run_id
                }"
                @click="
                    selectRun(run.run_id)
                "
            >

                <span class="run-id">
                    {{ run.run_id }}
                </span>


                <span
                    class="status"
                    :class="
                        getStatusClass(
                            run.status
                        )
                    "
                >
                    {{ run.status }}
                </span>


                <span>
                    {{
                        formatDate(
                            run.started_at
                        )
                    }}
                </span>


                <span>
                    {{
                        formatDate(
                            run.completed_at
                        )
                    }}
                </span>


                <span>
                    {{
                        formatDuration(run)
                    }}
                </span>

            </button>

        </div>

    </section>

</template>


<style scoped>

.run-list {
    background: white;

    border: 1px solid #e5e7eb;

    border-radius: 12px;

    padding: 24px;
}


/* =========================
   Header
========================= */

.section-header {
    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 20px;
}

.section-header h2 {
    margin: 0;

    font-size: 20px;

    color: #111827;
}

.section-header p {
    margin: 4px 0 0;

    color: #6b7280;

    font-size: 14px;
}


/* =========================
   Refresh Button
========================= */

.refresh-button {
    border: 1px solid #d1d5db;

    background: white;

    border-radius: 8px;

    padding: 8px 14px;

    cursor: pointer;

    font-size: 14px;
}

.refresh-button:hover {
    background: #f3f4f6;
}

.refresh-button:disabled {
    cursor: not-allowed;

    opacity: 0.6;
}


/* =========================
   Status Filters
========================= */

.status-filters {
    display: flex;

    gap: 8px;

    margin-bottom: 20px;
}

.filter-button {
    border: 1px solid #d1d5db;

    background: white;

    color: #374151;

    border-radius: 8px;

    padding: 8px 14px;

    font-size: 13px;

    font-weight: 500;

    cursor: pointer;
}

.filter-button:hover {
    background: #f3f4f6;
}

.filter-button.active {
    background: #111827;

    color: white;

    border-color: #111827;
}


/* =========================
   Summary
========================= */

.summary-grid {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 16px;

    margin-bottom: 16px;
}

.summary-card {
    border: 1px solid #e5e7eb;

    border-radius: 10px;

    padding: 18px;

    background: #f9fafb;
}

.summary-label {
    display: block;

    margin-bottom: 8px;

    color: #6b7280;

    font-size: 12px;

    font-weight: 600;

    text-transform: uppercase;
}

.summary-card strong {
    display: block;

    font-size: 28px;

    color: #111827;
}

.completed-card {
    border-left: 4px solid #22c55e;
}

.failed-card {
    border-left: 4px solid #ef4444;
}

.running-card {
    border-left: 4px solid #f59e0b;
}


/* =========================
   Observability
========================= */

.observability-grid {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 12px;

    margin-bottom: 24px;
}

.observability-card {
    border: 1px solid #e5e7eb;

    border-radius: 10px;

    padding: 14px;

    background: white;
}

.observability-card span {
    display: block;

    margin-bottom: 7px;

    color: #6b7280;

    font-size: 12px;
}

.observability-card strong {
    font-size: 20px;

    color: #111827;
}


/* =========================
   Table
========================= */

.runs-table {
    width: 100%;

    overflow-x: auto;
}

.table-header,
.run-row {
    display: grid;

    grid-template-columns:
        2fr
        0.9fr
        1.4fr
        1.4fr
        0.9fr;

    gap: 16px;

    align-items: center;

    min-width: 1000px;
}

.table-header {
    padding: 12px 16px;

    background: #f9fafb;

    border-bottom: 1px solid #e5e7eb;

    color: #6b7280;

    font-size: 12px;

    font-weight: 600;

    text-transform: uppercase;
}

.run-row {
    width: 100%;

    padding: 14px 16px;

    border: none;

    border-bottom: 1px solid #f3f4f6;

    background: white;

    text-align: left;

    cursor: pointer;

    font-size: 13px;

    color: #374151;
}

.run-row:hover {
    background: #f9fafb;
}

.run-row.selected {
    background: #eff6ff;
}

.run-id {
    font-family: monospace;

    color: #374151;

    word-break: break-all;
}


/* =========================
   Status
========================= */

.status {
    width: fit-content;

    padding: 4px 9px;

    border-radius: 999px;

    font-size: 12px;

    font-weight: 600;
}

.status-completed {
    background: #dcfce7;

    color: #166534;
}

.status-running {
    background: #fef3c7;

    color: #92400e;
}

.status-failed {
    background: #fee2e2;

    color: #991b1b;
}


/* =========================
   States
========================= */

.state-message {
    padding: 30px;

    text-align: center;

    color: #6b7280;
}

.state-message.error {
    color: #b91c1c;
}


/* =========================
   Responsive
========================= */

@media (max-width: 1000px) {

    .summary-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .observability-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

}


@media (max-width: 600px) {

    .summary-grid {
        grid-template-columns: 1fr;
    }

    .observability-grid {
        grid-template-columns: 1fr;
    }

    .status-filters {
        flex-wrap: wrap;
    }

}

</style>