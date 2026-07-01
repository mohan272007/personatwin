# API Documentation

Base URL (local): `http://localhost:8000`
Interactive Swagger UI: `http://localhost:8000/docs`

All endpoints accept/return JSON unless noted. `user_id` is obtained from
`/auth/google/mock` at login and stored client-side.

---

## POST /auth/google/mock
Demo login — creates or fetches a user by email.

**Query params:** `email` (required), `name` (optional)

```json
// Response
{ "user_id": "uuid", "name": "Ada Lovelace", "email": "ada@example.com" }
```

---

## POST /chat
Runs the full 6-agent pipeline for one message.

```json
// Request
{ "user_id": "uuid", "message": "What should I get my sister for her birthday?" }
```
```json
// Response
{
  "response": "Hey! Based on what I remember about her loving hiking gear...",
  "confidence_score": 0.78,
  "needs_clarification": false,
  "clarification_question": null,
  "explanation": "Confidence 78% = 0.82 memory relevance x0.5 + ...",
  "memories_used": [
    { "id": "uuid", "content": "...", "score": 0.83, "memory_type": "conversation", "created_at": "..." }
  ],
  "trace_id": "uuid"
}
```

---

## POST /upload/text
Teach the twin from pasted text (chat export, email, manual input).

```json
{ "user_id": "uuid", "text": "Hey! Just wanted to say...", "source": "manual_input" }
```

## POST /upload/file
`multipart/form-data`: `user_id`, `source`, `file` (.txt export).

Both return:
```json
{ "chunks_learned": 4, "trace_id": "uuid", "personality_profile": {...}, "style_profile": {...} }
```

---

## GET /memory/search?user_id=&q=&top_k=5
Semantic search over stored memories (RAG retrieval step).

## GET /memory/timeline?user_id=&limit=100
Chronological feed of all memories for the Memory Timeline page.

---

## GET /profile?user_id=
Returns merged personality + communication style profile.

## POST /profile
```json
{ "user_id": "uuid", "name": "Ada", "email": "ada@example.com", "avatar_url": "" }
```

---

## GET /preferences?user_id=
List permanent preferences.

## POST /preferences
```json
{ "user_id": "uuid", "key": "coffee_order", "value": "oat milk flat white" }
```

---

## GET /analytics?user_id=
Dashboard aggregate: total memories, total conversations, average
confidence, confidence trend (per turn), memory type breakdown, agent
activity counts, top topics.

## GET /analytics/logs?user_id=&limit=50
Raw per-agent activity feed (agent name, action, detail, duration_ms) —
powers the Agent Activity Logs panel and proves the multi-agent pipeline
actually executed for each turn.

---

## GET /health
Liveness check. `GET /` also reports whether `GEMINI_API_KEY` is active.
