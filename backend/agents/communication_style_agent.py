"""
agents/communication_style_agent.py
--------------------------------------
CommunicationStyleAgent

Builds a "style guide" for the user: tone label, favourite phrases,
greeting/sign-off patterns and punctuation habits. This is what lets the
ResponseGenerationAgent answer in a way that actually *sounds* like the
user, not just knows their facts.
"""

import json
import re
from collections import Counter
from database.db import SessionLocal, StyleProfile
from agents.base import BaseAgent

STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "i", "you", "to",
             "and", "of", "in", "it", "that", "for", "on", "with", "my", "me"}


def _extract_common_phrases(text: str, n: int = 2, top: int = 5):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    ngrams = [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]
    counts = Counter(ngrams)
    return [phrase for phrase, c in counts.most_common(top) if c > 1]


def _detect_tone(text: str) -> str:
    text_lower = text.lower()
    casual_hits = sum(text_lower.count(w) for w in ["lol", "haha", "gonna", "yeah", "hey", "!"])
    formal_hits = sum(text_lower.count(w) for w in ["regards", "sincerely", "dear", "kindly"])
    enthusiastic_hits = text.count("!") + len(re.findall(r"[\U0001F300-\U0001FAFF]", text))

    if formal_hits > casual_hits:
        return "formal"
    if enthusiastic_hits >= 2:
        return "enthusiastic"
    if casual_hits > 0:
        return "casual"
    return "neutral"


def _detect_greeting(text: str) -> str:
    first_line = text.strip().split("\n")[0][:30].lower()
    for g in ["hey", "hi", "hello", "dear", "yo", "greetings"]:
        if first_line.startswith(g):
            return g.capitalize()
    return "Hi"


def _detect_signoff(text: str) -> str:
    last_line = text.strip().split("\n")[-1][-30:].lower()
    for s in ["thanks", "cheers", "best", "regards", "later", "talk soon"]:
        if s in last_line:
            return s.capitalize()
    return ""


class CommunicationStyleAgent(BaseAgent):
    name = "CommunicationStyleAgent"

    def learn_from_text(self, user_id: str, text: str, trace_id: str = "") -> dict:
        tone = _detect_tone(text)
        phrases = _extract_common_phrases(text)
        greeting = _detect_greeting(text)
        signoff = _detect_signoff(text)
        punctuation = "expressive" if text.count("!") > 1 else "standard"

        db = SessionLocal()
        try:
            profile = db.get(StyleProfile, user_id)
            if profile is None:
                profile = StyleProfile(user_id=user_id)
                db.add(profile)

            profile.tone = tone  # most recent sample wins for tone (fast adaptation)
            existing_phrases = json.loads(profile.common_phrases_json or "[]")
            merged = list(dict.fromkeys(phrases + existing_phrases))[:10]
            profile.common_phrases_json = json.dumps(merged)
            if greeting != "Hi":
                profile.greeting_style = greeting
            if signoff:
                profile.sign_off_style = signoff
            profile.punctuation_style = punctuation

            db.commit()
            self.log("learn_from_text", f"Style updated -> tone={tone}, phrases={merged[:3]}")
            self.emit("Orchestrator", "STYLE_UPDATED", {"user_id": user_id, "tone": tone}, trace_id)

            return self._to_dict(profile)
        finally:
            db.close()

    def get_style_profile(self, user_id: str) -> dict:
        db = SessionLocal()
        try:
            profile = db.get(StyleProfile, user_id)
            if profile is None:
                return {
                    "tone": "neutral", "common_phrases": [],
                    "greeting_style": "Hi", "sign_off_style": "",
                    "punctuation_style": "standard",
                }
            return self._to_dict(profile)
        finally:
            db.close()

    @staticmethod
    def _to_dict(profile: StyleProfile) -> dict:
        return {
            "tone": profile.tone,
            "common_phrases": json.loads(profile.common_phrases_json or "[]"),
            "greeting_style": profile.greeting_style,
            "sign_off_style": profile.sign_off_style,
            "punctuation_style": profile.punctuation_style,
        }
