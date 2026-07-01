# Demo Script (2–3 minutes)

**Goal:** show judges a real multi-agent system with long-term memory and the
Confidence Score innovation — not just a chatbot with a persona prompt.

## 0. Setup (before judges arrive)
- Backend + frontend running (`docker compose up` or the two local dev servers)
- Have a short paragraph of "your" writing ready to paste (casual tone, a
  couple of exclamation marks, one clear preference — e.g. favorite coffee
  order or a hobby)

## 1. Landing → Login (15s)
- Open the landing page, point at the constellation hero and the "6
  specialized agents / A2A / Qdrant / live confidence score" strip.
- Sign in with any name/email — call out that this is a mock OAuth endpoint
  built to swap in real Google OAuth without touching the rest of the app.

## 2. Dashboard (15s)
- Point out **Twin readiness: 0%** — the twin is honest about knowing
  nothing yet. This sets up the Confidence Score payoff later.

## 3. Chat — before teaching (20s)
- Ask something personal: *"What should I get for lunch?"*
- Show the response comes back with a **low Confidence Score** and, ideally,
  a clarification question instead of a made-up answer.
- Click **"Why this response?"** — show the explanation string and that zero
  memories were used.

## 4. Settings — teach the twin (30s)
- Paste the prepared paragraph, click **Teach twin**.
- Call out live: this fans out to `PersonalityLearningAgent` and
  `CommunicationStyleAgent`, which update traits via exponential moving
  average — the twin **improves after every input**, not just once.

## 5. Chat — after teaching (30s)
- Ask the same or a related question again.
- Show the **Confidence Score jump**, and open "Why this response?" — now it
  cites real retrieved memories with similarity scores.
- Point out the reply's tone now matches the tone/greeting learned.

## 6. Memory Timeline (20s)
- Show the stored memories, filter by type, run a semantic search query
  (e.g. "coffee") and show relevance-ranked results from Qdrant.

## 7. Analytics (20s)
- Show the **confidence trend line climbing** as the twin learns.
- Scroll to **Agent Activity Logs** — show real per-agent, per-turn log
  entries with timing, proving the multi-agent pipeline genuinely executed
  (not a single LLM call pretending to be six agents).

## 8. Close (10s)
- One line: *"Every other 'AI persona' demo pretends to know you. PersonaTwin
  tells you when it doesn't — and shows its work."*

## Backup plan if Gemini API is rate-limited/offline
The offline template fallback still demonstrates the full agent pipeline,
memory retrieval, and Confidence Score — mention this is intentional
graceful degradation, not a bug.
