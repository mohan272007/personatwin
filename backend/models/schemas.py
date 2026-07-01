"""
models/schemas.py
------------------
Pydantic schemas shared across API routes.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):
    user_id: str
    message: str


class MemoryUsed(BaseModel):
    id: str
    content: str
    score: float
    memory_type: str
    created_at: str


class ChatResponse(BaseModel):
    response: str
    confidence_score: float
    needs_clarification: bool
    clarification_question: Optional[str] = None
    explanation: str
    memories_used: List[MemoryUsed]
    trace_id: str


class UploadTextRequest(BaseModel):
    user_id: str
    text: str
    source: str = "manual_input"


class MemorySearchResponse(BaseModel):
    id: str
    content: str
    score: float
    memory_type: str
    created_at: str


class ProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    traits: Dict[str, Any]
    tone: str
    formality_score: float
    positivity_score: float
    sample_count: int


class PreferenceItem(BaseModel):
    key: str
    value: str


class AnalyticsResponse(BaseModel):
    total_memories: int
    total_conversations: int
    avg_confidence: float
    confidence_trend: List[Dict[str, Any]]
    memory_type_breakdown: Dict[str, int]
    agent_activity_counts: Dict[str, int]
    top_topics: List[Dict[str, Any]]
