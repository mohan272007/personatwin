# Future Scope

- **Real Google OAuth** — replace `/auth/google/mock` with a full OAuth2
  consent + token exchange flow; the rest of the app is already `user_id`-based
  and needs no changes.
- **Distributed A2A** — move each agent to its own service (FastAPI or Google
  ADK runtime) communicating over HTTP/gRPC, using the same `A2AMessage`
  contract already defined in `orchestrator/a2a_protocol.py`.
- **Google ADK-native orchestration** — port `ADKOrchestrator` onto the actual
  Agent Development Kit runtime for built-in tracing, retries and tool-calling.
- **MCP tool servers** — expose calendar, email, and task-manager access as
  MCP servers the agents can call, so recommendations become actionable.
- **Multi-modal memory** — ingest PDFs, images, and voice notes; store CLIP /
  multi-modal embeddings alongside text in Qdrant.
- **Fine-tuned style embeddings** — replace heuristic style detection with a
  small fine-tuned model per user for more nuanced tone matching.
- **Proactive twin** — background job that surfaces unprompted insights
  ("you've mentioned being stressed about X three times this week").
- **Voice twin** — TTS trained/prompted to match the user's speaking cadence,
  for a true "digital extension of a person" experience.
- **Confidence Score calibration** — replace the current heuristic blend with
  a learned calibration model trained on user feedback (thumbs up/down per
  reply), improving trust in the score over time.
