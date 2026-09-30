from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import httpx

from backend.app.api.routes.runs import router as runs_router
from backend.app.api.routes.chat import router as chat_router


app = FastAPI(
    title="AI Research & Knowledge Assistant",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(runs_router)
app.include_router(chat_router)


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