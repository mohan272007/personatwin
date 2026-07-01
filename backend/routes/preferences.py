"""
routes/preferences.py
-------------------------
GET  /preferences  -> list all permanent preferences for a user
POST /preferences  -> upsert a preference key/value (Feature 3)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from database.db import SessionLocal, Preference
import datetime

router = APIRouter(prefix="/preferences", tags=["preferences"])


class PreferenceIn(BaseModel):
    user_id: str
    key: str
    value: str


@router.get("")
def list_preferences(user_id: str):
    db = SessionLocal()
    try:
        rows = db.query(Preference).filter(Preference.user_id == user_id).all()
        return [{"key": r.key, "value": r.value, "updated_at": r.updated_at.isoformat()} for r in rows]
    finally:
        db.close()


@router.post("")
def upsert_preference(req: PreferenceIn):
    db = SessionLocal()
    try:
        row = (
            db.query(Preference)
            .filter(Preference.user_id == req.user_id, Preference.key == req.key)
            .first()
        )
        if row is None:
            row = Preference(user_id=req.user_id, key=req.key, value=req.value)
            db.add(row)
        else:
            row.value = req.value
            row.updated_at = datetime.datetime.utcnow()
        db.commit()
        return {"status": "ok"}
    finally:
        db.close()
