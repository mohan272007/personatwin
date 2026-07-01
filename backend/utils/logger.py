"""
utils/logger.py
-----------------
Structured logger for multi-agent activity. Every agent hop within a
single conversation "trace" is recorded here, powering:
  - the Agent Activity Logs page
  - the explainability trail shown under each chat response
  - the /analytics endpoint's agent_activity_counts
"""

import time
from database.db import AgentLog, SessionLocal


class TraceLogger:
    """One instance per request/turn -- collects timed agent hops."""

    def __init__(self, user_id: str, trace_id: str):
        self.user_id = user_id
        self.trace_id = trace_id
        self.entries = []

    def log(self, agent_name: str, action: str, detail: str, duration_ms: float = 0.0):
        entry = {
            "agent_name": agent_name,
            "action": action,
            "detail": detail,
            "duration_ms": round(duration_ms, 2),
        }
        self.entries.append(entry)

        db = SessionLocal()
        try:
            db.add(
                AgentLog(
                    user_id=self.user_id,
                    trace_id=self.trace_id,
                    agent_name=agent_name,
                    action=action,
                    detail=detail,
                    duration_ms=duration_ms,
                )
            )
            db.commit()
        finally:
            db.close()

    def timed(self, agent_name: str, action: str):
        """Context manager: `with tracer.timed('MemoryAgent', 'retrieve'):`"""
        return _TimedBlock(self, agent_name, action)


class _TimedBlock:
    def __init__(self, tracer: TraceLogger, agent_name: str, action: str):
        self.tracer = tracer
        self.agent_name = agent_name
        self.action = action
        self.detail = ""

    def __enter__(self):
        self.start = time.time()
        return self

    def set_detail(self, detail: str):
        self.detail = detail

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start) * 1000
        detail = self.detail if not exc_type else f"ERROR: {exc_val}"
        self.tracer.log(self.agent_name, self.action, detail, duration_ms)
        return False
