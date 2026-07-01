"""
routes/chat.py
------------------
POST /chat
Runs the full agent pipeline (via ADKOrchestrator) for one user turn.
"""

from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from orchestrator.orchestrator import orchestrator

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = orchestrator.handle_message(req.user_id, req.message)
    return ChatResponse(**result)
