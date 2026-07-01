"""
database/db.py
----------------
SQLite metadata layer (via SQLAlchemy) for PersonaTwin AI.

Qdrant stores the VECTORS (embeddings) for semantic memory search.
SQLite stores the METADATA: users, memory records, personality profiles,
style profiles, preferences, agent activity logs and conversation history.

Splitting storage this way keeps the vector DB lean (embeddings + light
payload) while giving us relational querying / dashboards for free.
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import uuid

DATABASE_URL = "sqlite:///./persona_twin.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def gen_id() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, default="Demo User")
    email = Column(String, unique=True, index=True)
    avatar_url = Column(String, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PersonalityProfile(Base):
    """Continuously-updated personality profile (JSON blob of traits)."""
    __tablename__ = "personality_profiles"
    user_id = Column(String, primary_key=True)
    traits_json = Column(Text, default="{}")       # Big Five-ish trait scores
    values_json = Column(Text, default="[]")        # extracted opinions/values/preferences
    formality_score = Column(Float, default=0.5)
    positivity_score = Column(Float, default=0.5)
    avg_sentence_length = Column(Float, default=12.0)
    emoji_rate = Column(Float, default=0.0)
    sample_count = Column(Integer, default=0)       # how many texts learned from
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class StyleProfile(Base):
    """Communication style guide derived from user's writing samples."""
    __tablename__ = "style_profiles"
    user_id = Column(String, primary_key=True)
    tone = Column(String, default="neutral")
    common_phrases_json = Column(Text, default="[]")
    greeting_style = Column(String, default="Hi")
    sign_off_style = Column(String, default="")
    punctuation_style = Column(String, default="standard")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class Memory(Base):
    """Metadata mirror of a memory whose embedding lives in Qdrant."""
    __tablename__ = "memories"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, index=True)
    content = Column(Text)
    memory_type = Column(String, default="conversation")  # conversation | document | fact | preference
    source = Column(String, default="chat")
    importance = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Preference(Base):
    __tablename__ = "preferences"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, index=True)
    key = Column(String)
    value = Column(String)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, index=True)
    user_message = Column(Text)
    agent_response = Column(Text)
    confidence_score = Column(Float)
    needed_clarification = Column(Boolean, default=False)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AgentLog(Base):
    """Fine-grained A2A activity log -> powers the 'Agent Activity Logs' UI."""
    __tablename__ = "agent_logs"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, index=True)
    trace_id = Column(String, index=True)   # groups all agent hops for one turn
    agent_name = Column(String)
    action = Column(String)
    detail = Column(Text)
    duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
