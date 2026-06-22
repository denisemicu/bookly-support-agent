from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import run_bookly_agent

app = FastAPI(title="Bookly Support Agent API")

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://bookly-support-agent-xi.vercel.app",
    "https://bookly-support-agent-git-main-denise-s-org.vercel.app",
    "https://bookly-support-agent-arkx2vqf6-denise-s-org.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class AgentState(BaseModel):
    active_order_id: Optional[str] = None
    pending_action: Optional[str] = None
    pending_intent: Optional[str] = None
    return_reason: Optional[str] = None
    new_address: Optional[str] = None
    awaiting: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)
    state: Optional[AgentState] = None


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "bookly-support-agent",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "bookly-support-agent",
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "service": "bookly-support-agent",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    history = [message.model_dump() for message in request.history]
    state = request.state.model_dump() if request.state else None

    return run_bookly_agent(
        user_message=request.message,
        history=history,
        state=state,
    )