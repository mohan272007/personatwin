"""
routes/profile.py
---------------------
GET  /profile   -> merged personality + style profile for the dashboard
POST /profile   -> create/update basic user info (name, email)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from database.db import SessionLocal, User
from agents.personality_agent import PersonalityLearningAgent
from agents.communication_style_agent import CommunicationStyleAgent

router = APIRouter(prefix="/profile", tags=["profile"])
personality_agent = PersonalityLearningAgent()
style_agent = CommunicationStyleAgent()


class UpsertUser(BaseModel):
    user_id: str
    name: str = "Demo User"
    email: str = ""
    avatar_url: str = ""


@router.get("")
def get_profile(user_id: str):
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
    finally:
        db.close()

    personality = personality_agent.get_profile(user_id)
    style = style_agent.get_style_profile(user_id)

    return {
        "user_id": user_id,
        "name": user.name if user else "Demo User",
        "email": user.email if user else "",
        "avatar_url": user.avatar_url if user else "",
        "personality": personality,
        "style": style,
    }


@router.post("")
def upsert_profile(req: UpsertUser):
    db = SessionLocal()
    try:
        user = db.get(User, req.user_id)
        if user is None:
            user = User(id=req.user_id, name=req.name, email=req.email, avatar_url=req.avatar_url)
            db.add(user)
        else:
            user.name = req.name
            user.email = req.email
            user.avatar_url = req.avatar_url
        db.commit()
        return {"status": "ok"}
    finally:
        db.close()
