"""
orchestrator/orchestrator.py
--------------------------------
ADKOrchestrator

This is the "ADK Orchestrator" layer from the required architecture
diagram:  React -> FastAPI -> ADK Orchestrator -> Multi-Agent Layer.

It coordinates the six agents for every user turn, in this order:

  1. MemoryAgent            - retrieve top-k semantically similar memories
  2. PersonalityLearningAgent- fetch current personality profile
  3. CommunicationStyleAgent - fetch current style guide
  4. RecommendationAgent     - derive personalized recommendations
  5. ReasoningAgent          - compute Confidence Score + explanation
  6. ResponseGenerationAgent - produce the final reply (or clarification)

  ...then, for continuous learning:
  7. PersonalityLearningAgent + CommunicationStyleAgent re-learn from the
     user's new message
  8. MemoryAgent stores the new conversation turn as a memory

Every hop is logged through TraceLogger (-> Agent Activity Logs) and
published as an A2AMessage on the shared MessageBus (-> A2A protocol
requirement), even though agents currently run in-process.
"""

import uuid

from agents.memory_agent import MemoryAgent
from agents.personality_agent import PersonalityLearningAgent
from agents.communication_style_agent import CommunicationStyleAgent
from agents.recommendation_agent import RecommendationAgent
from agents.reasoning_agent import ReasoningAgent
from agents.response_agent import ResponseGenerationAgent
from utils.logger import TraceLogger
from database.db import SessionLocal, ConversationLog


class ADKOrchestrator:
    def __init__(self):
        self.memory_agent_cls = MemoryAgent
        self.personality_agent_cls = PersonalityLearningAgent
        self.style_agent_cls = CommunicationStyleAgent
        self.recommendation_agent_cls = RecommendationAgent
        self.reasoning_agent_cls = ReasoningAgent
        self.response_agent_cls = ResponseGenerationAgent

    def handle_message(self, user_id: str, message: str) -> dict:
        trace_id = str(uuid.uuid4())
        tracer = TraceLogger(user_id, trace_id)

        memory_agent = self.memory_agent_cls(tracer)
        personality_agent = self.personality_agent_cls(tracer)
        style_agent = self.style_agent_cls(tracer)
        recommendation_agent = self.recommendation_agent_cls(tracer)
        reasoning_agent = self.reasoning_agent_cls(tracer)
        response_agent = self.response_agent_cls(tracer)

        # 1. Semantic retrieval (RAG step)
        memories = memory_agent.retrieve_similar(user_id, message, top_k=5, trace_id=trace_id)

        # 2 & 3. Load learned personality + style
        personality = personality_agent.get_profile(user_id)
        style = style_agent.get_style_profile(user_id)

        # 4. Recommendations from memory patterns
        recommendations = recommendation_agent.generate_recommendations(
            user_id, memories, message, trace_id=trace_id
        )

        # 5. Reasoning + Confidence Score (the headline innovation)
        reasoning = reasoning_agent.reason(
            user_id, message, memories, personality, style, trace_id=trace_id
        )

        # 6. Final response generation
        reply = response_agent.generate(
            message, memories, personality, style, reasoning, trace_id=trace_id
        )
        if recommendations and not reasoning["needs_clarification"]:
            reply = f"{reply}\n\n(Note: {recommendations[0]})"

        # 7. Continuous learning: this new message teaches the twin more
        personality_agent.learn_from_text(user_id, message, trace_id=trace_id)
        style_agent.learn_from_text(user_id, message, trace_id=trace_id)

        # 8. Persist this turn as a new long-term memory
        memory_agent.store_memory(
            user_id, content=message, memory_type="conversation",
            source="chat", importance=0.5, trace_id=trace_id,
        )

        # Log the full conversational turn for /analytics + history
        db = SessionLocal()
        try:
            db.add(ConversationLog(
                user_id=user_id, user_message=message, agent_response=reply,
                confidence_score=reasoning["confidence_score"],
                needed_clarification=reasoning["needs_clarification"],
                explanation=reasoning["explanation"],
            ))
            db.commit()
        finally:
            db.close()

        return {
            "response": reply,
            "confidence_score": reasoning["confidence_score"],
            "needs_clarification": reasoning["needs_clarification"],
            "clarification_question": reasoning["clarification_question"],
            "explanation": reasoning["explanation"],
            "memories_used": memories,
            "trace_id": trace_id,
        }


# Singleton orchestrator used by the API routes
orchestrator = ADKOrchestrator()
