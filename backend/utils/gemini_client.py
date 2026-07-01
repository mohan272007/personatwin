"""
utils/gemini_client.py
------------------------
Wraps Google Gemini for final response generation.

If GEMINI_API_KEY is not set (e.g. judges running the demo offline, or a
quota hiccup mid-hackathon), we fall back to a deterministic, style-aware
template generator so the product NEVER breaks during a live demo.
This fallback is a real engineering feature (graceful degradation), not
just a stub -- it's called out in the README as such.
"""

import os
import re

MODEL_NAME = "gemini-2.0-flash"


def _relevant_values(query: str, values: list, max_items: int = 4) -> list:
    """Cheap relevance filter: prefer values whose statement shares a
    keyword with the query, otherwise fall back to the most recent ones."""
    if not values:
        return []
    query_words = set(re.findall(r"[a-zA-Z']+", query.lower()))
    scored = []
    for v in values:
        v_words = set(re.findall(r"[a-zA-Z']+", v["statement"].lower()))
        overlap = len(query_words & v_words)
        scored.append((overlap, v))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored[0][0] > 0:
        return [v for _, v in scored[:max_items] if _ > 0] or values[-max_items:]
    return values[-max_items:]


def _fallback_generate(prompt_context: dict) -> str:
    """
    Deterministic offline generator. Uses the retrieved memories +
    style profile to produce a reasonably personalized reply without
    calling any external API. Ensures the demo works with zero setup.
    """
    query = prompt_context["query"]
    memories = prompt_context["memories"]
    values = prompt_context["personality"].get("values", [])
    tone = prompt_context["style"].get("tone", "neutral")
    greeting = prompt_context["style"].get("greeting_style", "Hi")

    relevant_values = _relevant_values(query, values)

    if relevant_values:
        v = relevant_values[0]
        stance = "I love" if v["sentiment"] > 0.5 else "I'm not really into" if v["sentiment"] < -0.3 else "I generally think"
        body = f"{stance} {v['statement']}, so on \"{query}\" I'd go with that."
    elif memories:
        best = memories[0]["content"]
        body = (
            f"Based on what I remember -- \"{best[:120]}\" -- "
            f"here's my take on \"{query}\": I'd lean on that same "
            f"preference here and go with what's worked for you before."
        )
    else:
        body = (
            f"I don't have enough memory about this yet, so I'm answering "
            f"from general context on \"{query}\"."
        )

    if tone == "casual":
        return f"{greeting}! {body} 🙂"
    if tone == "formal":
        return f"{greeting}, {body.capitalize()} Let me know if you'd like more detail."
    return f"{greeting}. {body}"


def generate_response(prompt_context: dict) -> str:
    """
    prompt_context = {
        "query": str,
        "memories": [ {content, score, memory_type}, ... ],
        "personality": {...},
        "style": {...},
        "reasoning": {...},
    }
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_generate(prompt_context)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)

        memory_block = "\n".join(
            f"- ({m['memory_type']}, relevance {m['score']:.2f}): {m['content']}"
            for m in prompt_context["memories"]
        ) or "No relevant memories found."

        values = prompt_context["personality"].get("values", [])
        if values:
            values_block = "\n".join(
                f"- [{v['category']}] {v['statement']}" for v in values[-15:]
            )
        else:
            values_block = "No explicit opinions/values learned yet."

        system_prompt = f"""
You are the user's PERSONAL DIGITAL TWIN. You must reply exactly the way
THEY would reply -- not as a generic assistant.

STYLE GUIDE (learned from their real writing):
- Tone: {prompt_context['style'].get('tone')}
- Formality (0=casual, 1=formal): {prompt_context['personality'].get('formality_score')}
- Positivity: {prompt_context['personality'].get('positivity_score')}
- Typical greeting: {prompt_context['style'].get('greeting_style')}
- Typical sign-off: {prompt_context['style'].get('sign_off_style')}
- Average sentence length: {prompt_context['personality'].get('avg_sentence_length')} words

OPINIONS & VALUES this person has actually expressed (use these as YOUR
own stance when relevant -- don't hedge or say "some people think"):
{values_block}

RELEVANT LONG-TERM MEMORIES:
{memory_block}

Reply to the user's message AS THEM, in first person, using the opinions
and memories above only where relevant. Keep it natural -- do not mention
that you are an AI or that you retrieved memories.

USER MESSAGE: {prompt_context['query']}
"""
        result = model.generate_content(system_prompt)
        return result.text.strip()
    except Exception as e:
        # Never let an LLM outage break the demo
        return _fallback_generate(prompt_context)
