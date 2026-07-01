# PersonaTwin AI

**A multi-agent Personal Digital Twin that learns how you communicate, remembers
what matters to you, and answers exactly the way you would — with an honest,
transparent Confidence Score on every reply.**

Built for a one-day AI Hackathon. Fully working prototype, runs with zero API
keys (offline-safe fallback), upgrades automatically to real Gemini + Google
embeddings if a key is provided.

---

## Why it's different from a normal chatbot

Most "personal AI" demos are a chatbot with a system prompt bolted on. PersonaTwin
is built as an actual **multi-agent system** with long-term memory, continuous
learning, and — its headline feature — a **Confidence Score**:

> Every response PersonaTwin generates is scored on how closely it actually
> reflects the real user's learned personality, tone and memory. If confidence
> is low, the twin **asks a clarifying question instead of pretending to know you.**

This turns "hallucinated personality" from a silent failure mode into a visible,
measurable, and demo-able feature.

---

## Architecture

```
User
  │
  ▼
React Frontend  (chat, dashboard, memory timeline, analytics)
  │  REST / JSON
  ▼
FastAPI Backend  (routes: /chat /upload /memory/search /profile /preferences /analytics)
  │
  ▼
ADK Orchestrator   (orchestrator/orchestrator.py)
  │  A2A messages (orchestrator/a2a_protocol.py)
  ▼
Multi-Agent Layer
  ├── PersonalityLearningAgent   -> traits, formality, positivity
  ├── CommunicationStyleAgent    -> tone, phrases, greeting/sign-off
  ├── MemoryAgent                -> store + semantic retrieval
  ├── RecommendationAgent        -> pattern-based suggestions
  ├── ReasoningAgent             -> ⭐ Confidence Score + explainability
  └── ResponseGenerationAgent    -> final reply (Gemini or offline fallback)
  │
  ▼
Memory Layer — Qdrant (vector DB) + SQLite (metadata)
  │
  ▼
Gemini 2.0 Flash  (LLM + Google text-embedding-004)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
[`docs/SEQUENCE_DIAGRAM.md`](docs/SEQUENCE_DIAGRAM.md) for detailed diagrams.

### Why agents talk over A2A messages

Every inter-agent call is wrapped as a structured `A2AMessage` (sender,
receiver, intent, payload, trace_id) and published on an in-process
`MessageBus` — modeled after Google's Agent-to-Agent protocol. Agents run
in-process for the hackathon build, but the message contract is already
network-ready: swapping to real distributed A2A (agents as separate
services) only requires changing the transport in `MessageBus.send()`.

---

## The Confidence Score, in detail

`ReasoningAgent` (`backend/agents/reasoning_agent.py`) blends three signals:

| Signal | Weight | What it measures |
|---|---|---|
| Memory relevance | 50% | Avg. similarity of top retrieved memories from Qdrant |
| Learning volume | 30% | How many text samples the personality model has seen |
| Style completeness | 20% | Whether tone/phrases/greeting have been learned yet |

If the blended score falls below **45%**, the twin responds with a clarifying
question instead of a guess. Every chat response also exposes a **"Why this
response?"** panel in the UI showing the exact memories and math behind the
score — full explainability, not a black box.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, React Router, TailwindCSS, Recharts |
| Backend | Python, FastAPI |
| Orchestration | Custom ADK-style Orchestrator + A2A message protocol |
| Agents | 6 specialized Python agents (see above) |
| Memory | Qdrant (vector DB), SQLite (metadata), sentence-transformers / Google embeddings |
| LLM | Gemini 2.0 Flash (`google-generativeai`), offline template fallback |
| Auth | Mock Google OAuth endpoint (swap-in ready for real OAuth) |
| Deployment | Docker + docker-compose |

---

## Folder structure

```
PersonaTwin-AI/
├── backend/
│   ├── agents/            # 6 agents: personality, memory, style, recommendation, reasoning, response
│   ├── orchestrator/      # ADK orchestrator + A2A protocol
│   ├── memory/            # Qdrant vector store + embeddings
│   ├── models/            # Pydantic schemas
│   ├── database/          # SQLAlchemy models (SQLite)
│   ├── routes/            # /chat /upload /memory /profile /preferences /analytics
│   ├── utils/             # Gemini client, agent activity logger
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/          # Landing, Login, Dashboard, Chat, MemoryTimeline, Settings, Profile, Analytics
│   │   ├── components/     # Sidebar, ConfidenceBadge, MemoryCard, ConstellationCanvas
│   │   └── api/            # API client
│   └── package.json
├── docs/                   # Architecture, API docs, install guide, demo script, sequence diagram
├── docker-compose.yml
└── README.md
```

---

## Quick start (local, no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: add GEMINI_API_KEY to get real Gemini responses
uvicorn main:app --reload --port 8000
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Sign in with any name/email (mock Google OAuth) — no
credentials needed.

## Quick start (Docker)

```bash
cp backend/.env.example .env   # optional: set GEMINI_API_KEY
docker compose up --build
```
Frontend: http://localhost:5173 · Backend docs: http://localhost:8000/docs

Full installation notes: [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

---

## Demo flow (2 minutes)

See [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) for the full walkthrough. Short version:

1. Sign in → land on **Dashboard**, twin readiness is near 0%.
2. Go to **Settings**, paste a few casual sentences ("teach the twin").
3. Go to **Chat**, ask a question — watch the **Confidence Score** and click
   **"Why this response?"** to show the retrieved memories.
4. Go to **Memory Timeline**, run a semantic search.
5. Go to **Analytics**, show the confidence trend chart and live agent
   activity logs — proof the multi-agent pipeline actually ran.

---

## API reference

Full docs in [`docs/API_DOCS.md`](docs/API_DOCS.md) and interactive Swagger
UI at `/docs` once the backend is running.

| Endpoint | Method | Purpose |
|---|---|---|
| `/chat` | POST | Run full agent pipeline for one message |
| `/upload/text`, `/upload/file` | POST | Teach the twin from pasted text or a file |
| `/memory/search` | GET | Semantic memory search |
| `/memory/timeline` | GET | Chronological memory feed |
| `/profile` | GET/POST | Personality + style profile |
| `/preferences` | GET/POST | Permanent user preferences |
| `/analytics` | GET | Confidence trend, memory & agent stats |
| `/analytics/logs` | GET | Raw agent activity log feed |
| `/auth/google/mock` | POST | Demo login (real OAuth swap-in ready) |

---

## Future scope

See [`docs/FUTURE_SCOPE.md`](docs/FUTURE_SCOPE.md). Highlights: real Google
OAuth, distributed A2A over HTTP/gRPC, ADK-native agent runtime, voice twin,
multi-modal memory (images/PDFs), fine-tuned personality embeddings, proactive
notifications ("your twin noticed a pattern").

---

## Notes on scope for judges

This is a same-day hackathon build. To keep it demoable and reliable, we made
deliberate scope calls documented inline in the code:
- Google Embeddings + Gemini activate automatically if `GEMINI_API_KEY` is
  set; otherwise the system runs fully offline via local sentence-transformer
  embeddings and a style-aware template generator — **the app never breaks
  live on stage**.
- Google OAuth is mocked behind the same endpoint shape as real OAuth would
  use, so judges can log in instantly.
- Agents run in-process and communicate via structured A2A messages rather
  than separate network services — the protocol is real, the transport is
  simplified for a one-day build.
