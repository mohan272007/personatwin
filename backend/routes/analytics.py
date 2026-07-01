"""
routes/analytics.py
-----------------------
GET /analytics
Aggregates data for the Analytics page: memory counts, confidence-score
trend over time (ties directly into the Confidence Score innovation),
memory type breakdown, per-agent activity counts, and top topics.
"""

from fastapi import APIRouter
from collections import Counter
import re
from database.db import SessionLocal, Memory, ConversationLog, AgentLog

router = APIRouter(prefix="/analytics", tags=["analytics"])

STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "i", "you", "to",
             "and", "of", "in", "it", "that", "for", "on", "with", "my", "me"}


@router.get("")
def get_analytics(user_id: str):
    db = SessionLocal()
    try:
        memories = db.query(Memory).filter(Memory.user_id == user_id).all()
        conversations = (
            db.query(ConversationLog)
            .filter(ConversationLog.user_id == user_id)
            .order_by(ConversationLog.created_at.asc())
            .all()
        )
        agent_logs = db.query(AgentLog).filter(AgentLog.user_id == user_id).all()

        total_memories = len(memories)
        total_conversations = len(conversations)
        avg_confidence = (
            round(sum(c.confidence_score for c in conversations) / total_conversations, 3)
            if total_conversations else 0.0
        )
        confidence_trend = [
            {"turn": i + 1, "confidence": c.confidence_score, "timestamp": c.created_at.isoformat()}
            for i, c in enumerate(conversations)
        ]

        memory_type_breakdown = dict(Counter(m.memory_type for m in memories))
        agent_activity_counts = dict(Counter(a.agent_name for a in agent_logs))

        all_text = " ".join(m.content for m in memories)
        words = re.findall(r"[a-zA-Z']+", all_text.lower())
        words = [w for w in words if w not in STOPWORDS and len(w) > 3]
        top_topics = [{"topic": t, "count": c} for t, c in Counter(words).most_common(8)]

        return {
            "total_memories": total_memories,
            "total_conversations": total_conversations,
            "avg_confidence": avg_confidence,
            "confidence_trend": confidence_trend,
            "memory_type_breakdown": memory_type_breakdown,
            "agent_activity_counts": agent_activity_counts,
            "top_topics": top_topics,
        }
    finally:
        db.close()


@router.get("/logs")
def get_agent_logs(user_id: str, limit: int = 50):
    """Raw agent activity feed for the Agent Activity Logs panel."""
    db = SessionLocal()
    try:
        rows = (
            db.query(AgentLog)
            .filter(AgentLog.user_id == user_id)
            .order_by(AgentLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id, "trace_id": r.trace_id, "agent_name": r.agent_name,
                "action": r.action, "detail": r.detail, "duration_ms": r.duration_ms,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    finally:
        db.close()
