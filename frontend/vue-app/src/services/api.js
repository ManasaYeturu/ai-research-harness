const API_BASE_URL = "http://localhost:8000";

export async function getRuns(status = null) {
    const url = new URL(
        `${API_BASE_URL}/runs`
    );

    if (status) {
        url.searchParams.set(
            "status",
            status
        );
    }

    const response = await fetch(
        url.toString()
    );

    if (!response.ok) {
        throw new Error(
            "Failed to fetch runs"
        );
    }

    return response.json();
}

export async function getRunsSummary() {
    const response = await fetch(
        `${API_BASE_URL}/runs/summary`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch run summary");
    }

    return response.json();
}

export async function getRun(runId) {
    const response = await fetch(
        `${API_BASE_URL}/runs/${runId}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch run details");
    }

    return response.json();
}


export async function chat(question) {
    const response = await fetch(
        `${API_BASE_URL}/chat`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question
            })
        }
    );

    if (!response.ok) {
        let message = "Failed to send chat request";

        try {
            const errorData =
                await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }
        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }

    return response.json();
}