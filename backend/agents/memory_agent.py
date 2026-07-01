"""
agents/memory_agent.py
-------------------------
MemoryAgent

Owns the long-term memory lifecycle:
  - store_memory()   -> embeds + upserts into Qdrant, mirrors metadata in SQLite
  - retrieve_similar()-> semantic search (RAG retrieval step)
  - get_timeline()   -> chronological memory feed for the Memory Timeline page

This is the only agent that touches the vector store directly, keeping
the RAG plumbing in one place.
"""

from database.db import SessionLocal, Memory
from memory.vector_store import vector_store
from agents.base import BaseAgent


class MemoryAgent(BaseAgent):
    name = "MemoryAgent"

    def store_memory(self, user_id: str, content: str, memory_type: str = "conversation",
                      source: str = "chat", importance: float = 0.5, trace_id: str = "") -> str:
        db = SessionLocal()
        try:
            mem = Memory(
                user_id=user_id, content=content, memory_type=memory_type,
                source=source, importance=importance,
            )
            db.add(mem)
            db.commit()
            db.refresh(mem)

            vector_store.upsert_memory(
                memory_id=mem.id, user_id=user_id, content=content,
                memory_type=memory_type, created_at=mem.created_at.isoformat(),
                importance=importance,
            )
            self.log("store_memory", f"Stored '{memory_type}' memory ({len(content)} chars)")
            self.emit("Orchestrator", "MEMORY_STORED", {"memory_id": mem.id}, trace_id)
            return mem.id
        finally:
            db.close()

    def retrieve_similar(self, user_id: str, query: str, top_k: int = 5, trace_id: str = ""):
        results = vector_store.search(user_id=user_id, query=query, top_k=top_k)
        self.log("retrieve_similar", f"Retrieved {len(results)} memories for query '{query[:40]}'")
        self.emit("ReasoningAgent", "MEMORIES_RETRIEVED",
                  {"count": len(results)}, trace_id)
        return results

    def get_timeline(self, user_id: str, limit: int = 100):
        db = SessionLocal()
        try:
            rows = (
                db.query(Memory)
                .filter(Memory.user_id == user_id)
                .order_by(Memory.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": r.id, "content": r.content, "memory_type": r.memory_type,
                    "source": r.source, "importance": r.importance,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
        finally:
            db.close()

    def count_memories(self, user_id: str) -> int:
        db = SessionLocal()
        try:
            return db.query(Memory).filter(Memory.user_id == user_id).count()
        finally:
            db.close()
