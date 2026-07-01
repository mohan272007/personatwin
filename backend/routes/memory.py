"""
routes/memory.py
--------------------
GET /memory/search   -> semantic search over a user's memories (RAG retrieval)
GET /memory/timeline  -> chronological memory feed (Memory Timeline page)
"""

from fastapi import APIRouter, Query
from typing import List
from models.schemas import MemorySearchResponse
from agents.memory_agent import MemoryAgent

router = APIRouter(prefix="/memory", tags=["memory"])
memory_agent = MemoryAgent()


@router.get("/search", response_model=List[MemorySearchResponse])
def search_memory(user_id: str, q: str, top_k: int = 5):
    results = memory_agent.retrieve_similar(user_id, q, top_k=top_k)
    return results


@router.get("/timeline")
def memory_timeline(user_id: str, limit: int = 100):
    return memory_agent.get_timeline(user_id, limit=limit)
