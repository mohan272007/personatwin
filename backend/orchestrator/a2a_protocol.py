"""
orchestrator/a2a_protocol.py
------------------------------
A lightweight implementation of an Agent-to-Agent (A2A) messaging
protocol, modeled after Google's A2A spec (structured task envelopes
with sender/receiver/intent/payload instead of raw function calls).

For a same-day hackathon build we run all agents in-process (no network
hop), but every inter-agent call is still wrapped in an A2AMessage and
published on the MessageBus. This means:
  1. The architecture is genuinely multi-agent, not a monolith wearing
     agent-shaped function names.
  2. Swapping to real distributed A2A (agents as separate services
     speaking over HTTP/gRPC) later only requires changing the
     transport in MessageBus.send() -- the message contract is already
     network-ready.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import uuid
import datetime


@dataclass
class A2AMessage:
    sender: str
    receiver: str
    intent: str                     # e.g. "RETRIEVE_MEMORIES", "ANALYZE_STYLE"
    payload: Dict[str, Any]
    trace_id: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "trace_id": self.trace_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "intent": self.intent,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


class MessageBus:
    """In-process pub/sub transport for A2A messages."""

    def __init__(self):
        self.history: List[A2AMessage] = []

    def send(self, message: A2AMessage) -> A2AMessage:
        self.history.append(message)
        return message

    def trace(self, trace_id: str) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.history if m.trace_id == trace_id]


# Shared bus instance for the process
message_bus = MessageBus()
