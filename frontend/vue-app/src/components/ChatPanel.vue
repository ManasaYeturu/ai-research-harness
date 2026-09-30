<script setup>
import { ref } from "vue";

import {
    chat,
    getRun
} from "../services/api";

const question = ref("");
const messages = ref([]);
const loading = ref(false);
const error = ref("");

const emit = defineEmits([
    "run-created",
    "view-run"
]);

async function submitQuestion() {
    const trimmedQuestion =
        question.value.trim();

    if (
        !trimmedQuestion ||
        loading.value
    ) {
        return;
    }

    error.value = "";

    messages.value.push({
        role: "user",
        content: trimmedQuestion
    });

    question.value = "";

    loading.value = true;

    try {
        const response =
            await chat(trimmedQuestion);

        const runId =
            response.run_id;

        const assistantMessage = {
            role: "assistant",
            content: response.answer,
            runId: runId,
            sources: [],
            sourcesLoading: true,
            sourcesError: ""
        };

        messages.value.push(
            assistantMessage
        );

        /*
         * Tell App.vue that a new run was created.
         */
        emit(
            "run-created",
            runId
        );

        /*
         * Load structured source information
         * from the run details endpoint.
         */
        try {
            const run =
                await getRun(runId);

            assistantMessage.sources =
                run.sources || [];

            assistantMessage.sourcesLoading =
                false;

        } catch (sourceError) {
            assistantMessage.sourcesLoading =
                false;

            assistantMessage.sourcesError =
                sourceError.message ||
                "Unable to load sources.";
        }

    } catch (err) {
        error.value =
            err.message ||
            "Failed to process the question.";

    } finally {
        loading.value = false;
    }
}

/*
 * Clear only the frontend conversation.
 *
 * This does NOT delete runs from PostgreSQL.
 * Existing runs remain available in the Runs dashboard.
 */
function clearConversation() {
    messages.value = [];

    question.value = "";

    error.value = "";
}

/*
 * Tell App.vue which run should be displayed
 * in RunDetails.vue.
 */
function viewRun(runId) {
    if (!runId) {
        return;
    }

    emit(
        "view-run",
        runId
    );
}
</script>

<template>
    <section class="chat-panel">

        <!-- Chat header -->
        <div class="chat-header">

            <div>
                <h2>
                    AI Research Assistant
                </h2>

                <p>
                    Ask questions about the knowledge base.
                </p>
            </div>

            <!-- Clear conversation -->
            <button
                v-if="messages.length > 0"
                type="button"
                class="clear-button"
                @click="clearConversation"
            >
                Clear conversation
            </button>

        </div>

        <!-- Conversation -->
        <div class="conversation">

            <!-- Empty state -->
            <div
                v-if="messages.length === 0"
                class="empty-chat"
            >
                <div class="empty-title">
                    Start your research
                </div>

                <div class="empty-description">
                    Ask a question about the available
                    knowledge base.
                </div>
            </div>

            <!-- Messages -->
            <div
                v-for="(message, index) in messages"
                :key="index"
                class="message"
                :class="message.role"
            >

                <!-- Message label -->
                <div class="message-label">
                    {{
                        message.role === "user"
                            ? "You"
                            : "AI Research Assistant"
                    }}
                </div>

                <!-- Message content -->
                <div class="message-content">
                    {{ message.content }}
                </div>

                <!-- Assistant information -->
                <template
                    v-if="
                        message.role === 'assistant'
                    "
                >

                    <!-- Sources -->
                    <div class="sources-section">

                        <div class="sources-title">

                            <span class="sources-label">
                                Sources
                            </span>

                            <span class="source-count">
                                {{ message.sources.length }}
                                {{
                                    message.sources.length === 1
                                        ? "source"
                                        : "sources"
                                }}
                            </span>

                        </div>

                        <!-- Loading -->
                        <div
                            v-if="message.sourcesLoading"
                            class="sources-loading"
                        >
                            Loading sources...
                        </div>

                        <!-- Error -->
                        <div
                            v-else-if="
                                message.sourcesError
                            "
                            class="sources-error"
                        >
                            Unable to load sources:
                            {{ message.sourcesError }}
                        </div>

                        <!-- No sources -->
                        <div
                            v-else-if="
                                message.sources.length === 0
                            "
                            class="no-sources"
                        >
                            No sources were retrieved
                            for this run.
                        </div>

                        <!-- Sources -->
                        <div
                            v-else
                            class="sources-list"
                        >

                            <div
                                v-for="
                                    (source, sourceIndex)
                                    in message.sources
                                "
                                :key="sourceIndex"
                                class="source-card"
                            >

                                <div class="source-header">

                                    <div class="source-name">
                                        {{ source.source }}
                                    </div>

                                    <div class="source-chunk">
                                        Chunk
                                        {{ source.chunk_id }}
                                    </div>

                                </div>

                                <div class="source-score">

                                    <span>
                                        Relevance
                                    </span>

                                    <strong>
                                        {{
                                            Number(
                                                source.score
                                            ).toFixed(4)
                                        }}
                                    </strong>

                                </div>

                                <div class="source-content">
                                    {{ source.text }}
                                </div>

                            </div>

                        </div>

                    </div>

                    <!-- Run information -->
                    <div
                        v-if="message.runId"
                        class="run-reference"
                    >

                        <div class="run-id-row">

                            <div
                                class="run-id-information"
                            >

                                <span
                                    class="run-id-label"
                                >
                                    Run ID
                                </span>

                                <code>
                                    {{ message.runId }}
                                </code>

                            </div>

                            <!-- IMPORTANT:
                                 This emits view-run to App.vue -->
                            <button
                                type="button"
                                class="view-run-button"
                                @click="
                                    viewRun(
                                        message.runId
                                    )
                                "
                            >
                                View execution details
                            </button>

                        </div>

                    </div>

                </template>

            </div>

            <!-- Thinking -->
            <div
                v-if="loading"
                class="message assistant"
            >

                <div class="message-label">
                    AI Research Assistant
                </div>

                <div class="thinking">
                    Thinking...
                </div>

            </div>

        </div>

        <!-- Error -->
        <div
            v-if="error"
            class="error-message"
        >
            {{ error }}
        </div>

        <!-- Question form -->
        <form
            class="chat-form"
            @submit.prevent="submitQuestion"
        >

            <textarea
                v-model="question"
                placeholder="Ask a research question..."
                rows="3"
                :disabled="loading"
                @keydown.enter.exact.prevent="
                    submitQuestion
                "
            ></textarea>

            <div class="chat-actions">

                <span class="hint">
                    The agent may use tools and
                    knowledge retrieval.
                </span>

                <button
                    type="submit"
                    :disabled="
                        loading ||
                        !question.trim()
                    "
                >
                    {{
                        loading
                            ? "Thinking..."
                            : "Ask"
                    }}
                </button>

            </div>

        </form>

    </section>
</template>

<style scoped>
.chat-panel {
    width: 100%;
    box-sizing: border-box;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
}

/* Header */

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}

.chat-header h2 {
    margin: 0;
    font-size: 20px;
    color: #111827;
}

.chat-header p {
    margin: 5px 0 0;
    color: #6b7280;
    font-size: 14px;
}

/* Clear button */

.clear-button {
    flex-shrink: 0;
    border: 1px solid #d1d5db;
    border-radius: 7px;
    padding: 8px 12px;
    background: white;
    color: #4b5563;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
}

.clear-button:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

/* Conversation */

.conversation {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 4px;
}

.empty-chat {
    text-align: center;
    padding: 50px 20px;
    color: #6b7280;
}

.empty-title {
    font-size: 18px;
    font-weight: 600;
    color: #374151;
}

.empty-description {
    margin-top: 6px;
    font-size: 14px;
}

/* Messages */

.message {
    max-width: 85%;
    padding: 14px 16px;
    border-radius: 12px;
}

.message.user {
    align-self: flex-end;
    background: #111827;
    color: white;
}

.message.assistant {
    align-self: flex-start;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    color: #111827;
}

.message-label {
    margin-bottom: 6px;
    font-size: 12px;
    font-weight: 600;
}

.message.user .message-label {
    color: #d1d5db;
}

.message.assistant .message-label {
    color: #6b7280;
}

.message-content {
    line-height: 1.7;
    white-space: pre-wrap;
    text-align: left;
    font-size: 15px;
}

/* Sources */

.sources-section {
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid #e5e7eb;
}

.sources-title {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    font-size: 14px;
}

.sources-label {
    font-weight: 600;
    color: #111827;
}

.source-count {
    margin-left: 10px;
    color: #6b7280;
    font-size: 12px;
    font-weight: 500;
}

.sources-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.source-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px;
    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}

.source-card:hover {
    border-color: #d1d5db;
    box-shadow:
        0 2px 6px rgba(0, 0, 0, 0.04);
}

.source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.source-name {
    font-size: 13px;
    font-weight: 600;
    color: #111827;
}

.source-chunk {
    font-size: 11px;
    color: #6b7280;
    white-space: nowrap;
}

.source-score {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
    font-size: 11px;
    color: #6b7280;
}

.source-score strong {
    color: #374151;
    font-weight: 600;
}

.source-content {
    padding: 12px;
    background: #f9fafb;
    border-radius: 6px;
    color: #374151;
    font-size: 12px;
    line-height: 1.6;
    white-space: pre-wrap;
    text-align: left;
}

.sources-loading {
    color: #6b7280;
    font-size: 12px;
    font-style: italic;
    padding: 8px 0;
}

.sources-error {
    color: #b91c1c;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 6px;
    padding: 10px;
    font-size: 12px;
}

.no-sources {
    color: #6b7280;
    font-size: 12px;
    padding: 8px 0;
}

/* Run reference */

.run-reference {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #e5e7eb;
}

.run-id-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}

.run-id-information {
    display: flex;
    flex-direction: column;
    min-width: 0;
    gap: 4px;
}

.run-id-label {
    font-size: 11px;
    color: #6b7280;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.run-id-information code {
    font-family: monospace;
    font-size: 11px;
    color: #4b5563;
    word-break: break-all;
}

/* View execution button */

.view-run-button {
    flex-shrink: 0;
    border: 1px solid #d1d5db;
    border-radius: 7px;
    padding: 8px 12px;
    background: white;
    color: #374151;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    transition:
        background 0.15s ease,
        border-color 0.15s ease;
}

.view-run-button:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

/* Thinking */

.thinking {
    color: #6b7280;
    font-style: italic;
}

/* Form */

.chat-form {
    margin-top: 20px;
}

.chat-form textarea {
    width: 100%;
    min-height: 80px;
    resize: vertical;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 13px 14px;
    outline: none;
    color: #111827;
    background: white;
    box-sizing: border-box;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
}

.chat-form textarea::placeholder {
    color: #9ca3af;
}

.chat-form textarea:focus {
    border-color: #6b7280;
    box-shadow:
        0 0 0 3px rgba(17, 24, 39, 0.05);
}

.chat-form textarea:disabled {
    background: #f9fafb;
}

.chat-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    gap: 16px;
}

.hint {
    color: #6b7280;
    font-size: 12px;
}

.chat-actions button {
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    background: #111827;
    color: white;
    cursor: pointer;
    font-weight: 600;
}

.chat-actions button:hover {
    background: #1f2937;
}

.chat-actions button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

/* Error */

.error-message {
    margin-top: 16px;
    padding: 12px;
    border-radius: 8px;
    background: #fee2e2;
    color: #991b1b;
    font-size: 14px;
}

/* Mobile */

@media (max-width: 600px) {
    .chat-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .clear-button {
        width: 100%;
    }

    .message {
        max-width: 95%;
    }

    .chat-actions {
        align-items: stretch;
        flex-direction: column;
    }

    .chat-actions button {
        width: 100%;
    }

    .source-header {
        align-items: flex-start;
        flex-direction: column;
        gap: 4px;
    }

    .run-id-row {
        align-items: stretch;
        flex-direction: column;
    }

    .view-run-button {
        width: 100%;
    }
}
</style>