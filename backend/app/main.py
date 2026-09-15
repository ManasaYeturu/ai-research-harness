from fastapi import FastAPI
import httpx

app = FastAPI(
    title="AI Research & Knowledge Assistant",
    version="0.1.0"
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/ask")
async def ask_question(question: str):

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": question,
                "stream": False
            },
            timeout=120.0
        )

    response.raise_for_status()

    result = response.json()

    return {
        "question": question,
        "answer": result["response"]
    }