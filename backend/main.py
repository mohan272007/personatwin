"""
main.py
----------
PersonaTwin AI - FastAPI backend entrypoint.

Architecture (per the required diagram):
  React Frontend -> FastAPI Backend -> ADK Orchestrator -> Multi-Agent Layer
  -> Memory Layer (Qdrant) -> Gemini

Run with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

from database.db import init_db, SessionLocal, User
from routes import chat, upload, memory, profile, preferences, analytics

app = FastAPI(
    title="PersonaTwin AI",
    description="A multi-agent Personal Digital Twin -- learns your personality, "
                 "tone and memories, then responds exactly the way you would.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # relaxed for hackathon demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(memory.router)
app.include_router(profile.router)
app.include_router(preferences.router)
app.include_router(analytics.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": "PersonaTwin AI",
        "status": "running",
        "gemini_enabled": bool(os.getenv("GEMINI_API_KEY")),
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# --- Mock Google OAuth login (demo-safe) ---------------------------------
# A hackathon-safe stand-in for full Google OAuth. It creates/returns a
# deterministic user_id for the given email, so the rest of the app can be
# built and demoed without needing real OAuth client credentials configured.
# Swapping in real Google OAuth only requires replacing this endpoint with
# a redirect to Google's consent screen + token exchange -- the rest of the
# system (routes/profile.py etc.) is already user_id-based and unaffected.
@app.post("/auth/google/mock")
def mock_google_login(email: str, name: str = "Demo User"):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(id=str(uuid.uuid4()), name=name, email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
        return {"user_id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()
