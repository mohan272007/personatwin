"""
agents/response_agent.py
----------------------------
ResponseGenerationAgent

Final agent in the pipeline. Assembles everything the other agents
produced (memories, personality, style, reasoning) into a single prompt
context and calls Gemini (utils/gemini_client) to produce the reply --
or the clarification question, if the ReasoningAgent flagged low
confidence.
"""

from agents.base import BaseAgent
from utils.gemini_client import generate_response


class ResponseGenerationAgent(BaseAgent):
    name = "ResponseGenerationAgent"

    def generate(self, query: str, memories: list, personality: dict,
                 style: dict, reasoning: dict, trace_id: str = "") -> str:

        if reasoning["needs_clarification"]:
            self.log("generate", "Low confidence -> asked clarification question instead of guessing")
            return reasoning["clarification_question"]

        prompt_context = {
            "query": query,
            "memories": memories,
            "personality": personality,
            "style": style,
            "reasoning": reasoning,
        }
        reply = generate_response(prompt_context)
        self.log("generate", f"Generated response ({len(reply)} chars) using Gemini/fallback")
        return reply
