"""
routes/upload.py
--------------------
POST /upload
Accepts either:
  - a raw text file (.txt) upload -- e.g. an exported chat/email log, or
  - a JSON body { user_id, text, source } for manual paste-in input.

The text is chunked, then fed through PersonalityLearningAgent,
CommunicationStyleAgent, and MemoryAgent so the twin learns from it
immediately (Feature 1: learn from uploaded chats/docs/emails/manual input).
"""

from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from models.schemas import UploadTextRequest
from agents.personality_agent import PersonalityLearningAgent
from agents.communication_style_agent import CommunicationStyleAgent
from agents.memory_agent import MemoryAgent
from utils.logger import TraceLogger
import uuid

router = APIRouter(tags=["upload"])

CHUNK_SIZE = 500  # characters per learning chunk


def _chunk(text: str, size: int = CHUNK_SIZE):
    text = text.strip()
    return [text[i:i + size] for i in range(0, len(text), size) if text[i:i + size].strip()]


def _ingest(user_id: str, text: str, source: str) -> dict:
    trace_id = str(uuid.uuid4())
    tracer = TraceLogger(user_id, trace_id)
    personality_agent = PersonalityLearningAgent(tracer)
    style_agent = CommunicationStyleAgent(tracer)
    memory_agent = MemoryAgent(tracer)

    chunks = _chunk(text)
    for chunk in chunks:
        personality_agent.learn_from_text(user_id, chunk, trace_id=trace_id)
        style_agent.learn_from_text(user_id, chunk, trace_id=trace_id)
        memory_agent.store_memory(
            user_id, content=chunk, memory_type="document",
            source=source, importance=0.6, trace_id=trace_id,
        )

    return {
        "chunks_learned": len(chunks),
        "trace_id": trace_id,
        "personality_profile": personality_agent.get_profile(user_id),
        "style_profile": style_agent.get_style_profile(user_id),
    }


@router.post("/upload/text")
def upload_text(req: UploadTextRequest):
    """Manual paste-in input (Feature 1)."""
    return _ingest(req.user_id, req.text, req.source)


@router.post("/upload/file")
async def upload_file(user_id: str = Form(...), source: str = Form("document"),
                       file: UploadFile = File(...)):
    """Upload a .txt export of chats/emails/documents."""
    raw = await file.read()
    text = raw.decode("utf-8", errors="ignore")
    return _ingest(user_id, text, source)
