"""
agents/recommendation_agent.py
---------------------------------
RecommendationAgent

Looks across retrieved + historical memories to surface lightweight,
explainable recommendations ("You've mentioned X three times, want me to
factor that in?"). Kept heuristic (frequency + recency) rather than a
second LLM call, to stay fast and cheap for a live demo.
"""

import re
from collections import Counter
from agents.base import BaseAgent

STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "i", "you", "to",
             "and", "of", "in", "it", "that", "for", "on", "with", "my", "me",
             "this", "have", "do", "did", "be", "so", "but", "at", "as"}


class RecommendationAgent(BaseAgent):
    name = "RecommendationAgent"

    def generate_recommendations(self, user_id: str, memories: list, query: str, trace_id: str = "") -> list:
        all_text = " ".join(m["content"] for m in memories)
        words = re.findall(r"[a-zA-Z']+", all_text.lower())
        words = [w for w in words if w not in STOPWORDS and len(w) > 3]
        top_topics = [t for t, c in Counter(words).most_common(5) if c >= 2]

        recommendations = []
        for topic in top_topics[:3]:
            recommendations.append(
                f"Since you've mentioned '{topic}' before, I factored that preference into this answer."
            )

        if not recommendations and memories:
            recommendations.append(
                "This is based on the closest matching memory I have, though it's not a strong pattern yet."
            )

        self.log("generate_recommendations", f"Derived {len(recommendations)} recommendation(s) from {len(memories)} memories")
        self.emit("ReasoningAgent", "RECOMMENDATIONS_READY", {"count": len(recommendations)}, trace_id)
        return recommendations
