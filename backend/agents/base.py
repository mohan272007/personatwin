"""
agents/base.py
----------------
Base class for all PersonaTwin agents. Standardizes how an agent sends
A2A messages and logs its activity, so every concrete agent
(PersonalityLearningAgent, MemoryAgent, ...) only implements its domain
logic.
"""

from orchestrator.a2a_protocol import A2AMessage, message_bus


class BaseAgent:
    name = "BaseAgent"

    def __init__(self, tracer=None):
        self.tracer = tracer

    def emit(self, receiver: str, intent: str, payload: dict, trace_id: str):
        """Publish an A2A message to another agent / the orchestrator."""
        msg = A2AMessage(
            sender=self.name,
            receiver=receiver,
            intent=intent,
            payload=payload,
            trace_id=trace_id,
        )
        return message_bus.send(msg)

    def log(self, action: str, detail: str, duration_ms: float = 0.0):
        if self.tracer:
            self.tracer.log(self.name, action, detail, duration_ms)
