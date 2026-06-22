from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_bookly_agent

app = FastAPI(title="Bookly Support Agent API")

# Frontends allowed to call this API.
# Add your real Vercel URL here later, once we deploy the backend.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "bookly-support-agent",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    history = [message.model_dump() for message in request.history]

    return run_bookly_agent(
        user_message=request.message,
        history=history,
    )