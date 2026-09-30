<script setup>
import { ref } from "vue";

import ChatPanel from "./components/ChatPanel.vue";
import RunList from "./components/RunList.vue";
import RunDetails from "./components/RunDetails.vue";

const selectedRunId = ref(null);

function handleRunSelected(runId) {
    selectedRunId.value = runId;
}

function handleRunCreated(runId) {
    selectedRunId.value = runId;
}
</script>

<template>
    <div class="app">
        <header class="app-header">
            <div>
                <h1>
                    AI Research & Knowledge Assistant
                </h1>

                <p>
                    AI-powered research assistant with
                    knowledge retrieval, tools, evaluation,
                    and execution monitoring.
                </p>
            </div>
        </header>

        <main class="main-content">
            <!-- Chat -->
            <ChatPanel
                @run-created="handleRunCreated"
                @view-run="handleRunSelected"
            />

            <!-- Runs dashboard -->
            <RunList
                @select-run="handleRunSelected"
            />

            <!-- Selected run details -->
            <RunDetails
                :run-id="selectedRunId"
            />
        </main>
    </div>
</template>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background: #f3f4f6;
    color: #111827;
}

button,
textarea,
input {
    font-family: inherit;
}

.app {
    min-height: 100vh;
}

.app-header {
    background: #111827;
    color: white;
    padding: 28px 32px;
}

.app-header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
}

.app-header p {
    margin: 7px 0 0;
    color: #d1d5db;
    font-size: 14px;
    line-height: 1.5;
}

.main-content {
    width: min(1200px, calc(100% - 32px));
    margin: 24px auto;
}

@media (max-width: 600px) {
    .app-header {
        padding: 22px 18px;
    }

    .app-header h1 {
        font-size: 20px;
    }

    .main-content {
        width: calc(100% - 20px);
        margin: 16px auto;
    }
}
</style>