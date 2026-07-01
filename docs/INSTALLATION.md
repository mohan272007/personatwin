# Installation Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Docker + Docker Compose
- (Optional) A Gemini API key from https://aistudio.google.com/apikey — the
  app runs fully without one.

## Option A — Run locally (recommended for hackathon judging speed)

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit and add GEMINI_API_KEY if you have one
uvicorn main:app --reload --port 8000
```
Verify: open http://localhost:8000/docs — you should see the Swagger UI.

First run downloads the local embedding model (`all-MiniLM-L6-v2`, ~80MB) if
`GEMINI_API_KEY` is not set — this needs internet once, then works offline.

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173, sign in with any name/email.

## Option B — Docker Compose (closer to a "production" deployment)

```bash
# from the project root
cp backend/.env.example .env    # optional, add GEMINI_API_KEY
docker compose up --build
```
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs
- Qdrant dashboard: http://localhost:6333/dashboard

This spins up a real Qdrant server container instead of the embedded local
mode — useful to show judges the vector DB directly.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Frontend shows "Backend unreachable" | Confirm `uvicorn` is running on port 8000 and CORS isn't blocked |
| First chat message is slow | Local embedding model is downloading/loading on first use |
| Gemini errors in logs | App auto-falls back to the offline template generator — safe to ignore during a demo |
| Qdrant lock error running backend twice | Only one process can open the embedded local Qdrant at `./qdrant_data` at a time — stop other instances, or set `QDRANT_URL` to a running Qdrant server |
