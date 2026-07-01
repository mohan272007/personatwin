"""
agents/personality_agent.py
------------------------------
PersonalityLearningAgent

Learns a lightweight personality profile from raw text samples
(chats, emails, documents, manual input). Uses fast, transparent
heuristics (no black-box classifier) so results are explainable --
judges can see exactly why a trait score moved.

Traits tracked (loosely inspired by Big Five, simplified for a 1-day build):
  - openness        : vocabulary diversity, curiosity words
  - conscientiousness: planning words, structured punctuation
  - extraversion     : exclamation/emoji rate, social words
  - agreeableness    : positive/polite words
  - formality_score  : slang vs. formal phrasing
  - positivity_score : positive vs negative sentiment words

Every new sample updates the profile via an exponential moving average
so the twin "continuously improves after every conversation" (Feature 7)
instead of being overwritten.
"""

import json
import re
from database.db import SessionLocal, PersonalityProfile
from agents.base import BaseAgent

POSITIVE_WORDS = {"great", "love", "awesome", "good", "happy", "excited", "thanks",
                   "nice", "amazing", "glad", "cool", "perfect", "yes", "sure"}
NEGATIVE_WORDS = {"bad", "hate", "annoyed", "sad", "angry", "no", "never",
                   "worst", "terrible", "sorry", "problem", "issue"}
FORMAL_MARKERS = {"regards", "dear", "sincerely", "kindly", "please find",
                   "furthermore", "therefore", "hereby"}
CASUAL_MARKERS = {"lol", "haha", "gonna", "wanna", "yeah", "u ", "btw", "omg", "hey"}
CURIOSITY_WORDS = {"why", "how", "what if", "wonder", "curious", "explore", "idea"}
PLANNING_WORDS = {"schedule", "plan", "deadline", "todo", "organize", "list", "step"}
SOCIAL_WORDS = {"we", "team", "friend", "everyone", "together", "meet", "call"}

EMA_ALPHA = 0.3  # weight given to the newest sample vs. history

# Patterns that signal a stated opinion, value, or preference -- the raw
# material for "what this person actually believes/likes", not just how
# they phrase things. Each match becomes a structured entry in
# PersonalityProfile.values_json.
OPINION_PATTERNS = [
    (re.compile(r"\bi (?:really |absolutely |honestly )?love ([^.!?\n]{3,60})", re.I), "likes", 0.9),
    (re.compile(r"\bi (?:really |absolutely |honestly )?hate ([^.!?\n]{3,60})", re.I), "dislikes", -0.9),
    (re.compile(r"\bi (?:really |honestly )?prefer ([^.!?\n]{3,60})", re.I), "prefers", 0.6),
    (re.compile(r"\bi (?:really |honestly |strongly )?(?:think|believe) (?:that )?([^.!?\n]{3,80})", re.I), "believes", 0.0),
    (re.compile(r"\bmy favou?rite [a-z ]{0,20} is ([^.!?\n]{2,50})", re.I), "favorite", 0.9),
    (re.compile(r"\bi (?:can't stand|dislike) ([^.!?\n]{3,60})", re.I), "dislikes", -0.7),
    (re.compile(r"\bi (?:always|usually) ([^.!?\n]{3,60})", re.I), "habit", 0.3),
]

MAX_STORED_VALUES = 25


def _extract_opinions(text: str) -> list:
    """Pull explicit first-person opinion/value/preference statements out of text."""
    found = []
    for pattern, category, sentiment in OPINION_PATTERNS:
        for match in pattern.finditer(text):
            statement = match.group(1).strip().rstrip(",;:")
            if len(statement) < 3:
                continue
            found.append({
                "category": category,
                "statement": statement,
                "sentiment": sentiment,
            })
    return found


def _rate(text_lower: str, vocab: set) -> float:
    words = text_lower.split()
    if not words:
        return 0.0
    hits = sum(1 for w in vocab if w in text_lower)
    return min(hits / max(len(words) / 8, 1), 1.0)


class PersonalityLearningAgent(BaseAgent):
    name = "PersonalityLearningAgent"

    def analyze_text(self, text: str) -> dict:
        text_lower = text.lower()
        sentences = re.split(r"[.!?]+", text)
        sentences = [s for s in sentences if s.strip()]
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else len(text.split())
        )
        emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", text))
        exclam_rate = text.count("!") / max(len(sentences), 1)

        formality = _rate(text_lower, FORMAL_MARKERS) - _rate(text_lower, CASUAL_MARKERS)
        formality_score = max(0.0, min(1.0, 0.5 + formality))

        pos = _rate(text_lower, POSITIVE_WORDS)
        neg = _rate(text_lower, NEGATIVE_WORDS)
        positivity_score = max(0.0, min(1.0, 0.5 + (pos - neg)))

        traits = {
            "openness": round(_rate(text_lower, CURIOSITY_WORDS), 2),
            "conscientiousness": round(_rate(text_lower, PLANNING_WORDS), 2),
            "extraversion": round(min(1.0, exclam_rate + emoji_count * 0.1), 2),
            "agreeableness": round(pos, 2),
            "sociability": round(_rate(text_lower, SOCIAL_WORDS), 2),
        }

        return {
            "traits": traits,
            "formality_score": round(formality_score, 2),
            "positivity_score": round(positivity_score, 2),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "emoji_rate": round(emoji_count / max(len(text.split()), 1), 3),
        }

    def learn_from_text(self, user_id: str, text: str, trace_id: str = "") -> dict:
        """Ingest one text sample and update the persisted profile (EMA)."""
        new_stats = self.analyze_text(text)

        db = SessionLocal()
        try:
            profile = db.get(PersonalityProfile, user_id)
            if profile is None:
                profile = PersonalityProfile(user_id=user_id, sample_count=0)
                db.add(profile)
                old_traits = {}
                old_values = []
            else:
                old_traits = json.loads(profile.traits_json or "{}")
                old_values = json.loads(profile.values_json or "[]")

            merged_traits = {}
            for k, v in new_stats["traits"].items():
                old_v = old_traits.get(k, v)
                merged_traits[k] = round(old_v * (1 - EMA_ALPHA) + v * EMA_ALPHA, 3)

            # Merge newly-extracted opinions/values, deduping near-identical
            # statements and keeping the most recent MAX_STORED_VALUES.
            new_opinions = _extract_opinions(text)
            existing_statements = {v["statement"].lower() for v in old_values}
            for op in new_opinions:
                if op["statement"].lower() not in existing_statements:
                    old_values.append(op)
                    existing_statements.add(op["statement"].lower())
            merged_values = old_values[-MAX_STORED_VALUES:]

            profile.traits_json = json.dumps(merged_traits)
            profile.values_json = json.dumps(merged_values)
            profile.formality_score = round(
                profile.formality_score * (1 - EMA_ALPHA) + new_stats["formality_score"] * EMA_ALPHA, 3
            ) if profile.sample_count else new_stats["formality_score"]
            profile.positivity_score = round(
                profile.positivity_score * (1 - EMA_ALPHA) + new_stats["positivity_score"] * EMA_ALPHA, 3
            ) if profile.sample_count else new_stats["positivity_score"]
            profile.avg_sentence_length = round(
                profile.avg_sentence_length * (1 - EMA_ALPHA) + new_stats["avg_sentence_length"] * EMA_ALPHA, 2
            ) if profile.sample_count else new_stats["avg_sentence_length"]
            profile.emoji_rate = round(
                profile.emoji_rate * (1 - EMA_ALPHA) + new_stats["emoji_rate"] * EMA_ALPHA, 4
            ) if profile.sample_count else new_stats["emoji_rate"]
            profile.sample_count += 1

            db.commit()
            self.log("learn_from_text",
                      f"Updated personality profile (sample #{profile.sample_count}, "
                      f"+{len(new_opinions)} opinion(s) found, {len(merged_values)} total)")
            self.emit("Orchestrator", "PERSONALITY_UPDATED",
                      {"user_id": user_id, "sample_count": profile.sample_count}, trace_id)

            return {
                "traits": merged_traits,
                "values": merged_values,
                "formality_score": profile.formality_score,
                "positivity_score": profile.positivity_score,
                "avg_sentence_length": profile.avg_sentence_length,
                "emoji_rate": profile.emoji_rate,
                "sample_count": profile.sample_count,
            }
        finally:
            db.close()

    def get_profile(self, user_id: str) -> dict:
        db = SessionLocal()
        try:
            profile = db.get(PersonalityProfile, user_id)
            if profile is None:
                return {
                    "traits": {}, "values": [], "formality_score": 0.5, "positivity_score": 0.5,
                    "avg_sentence_length": 12.0, "emoji_rate": 0.0, "sample_count": 0,
                }
            return {
                "traits": json.loads(profile.traits_json or "{}"),
                "values": json.loads(profile.values_json or "[]"),
                "formality_score": profile.formality_score,
                "positivity_score": profile.positivity_score,
                "avg_sentence_length": profile.avg_sentence_length,
                "emoji_rate": profile.emoji_rate,
                "sample_count": profile.sample_count,
            }
        finally:
            db.close()
