"""
Database setup (SQLite for local dev, swappable for Postgres/Supabase later).

Tracks metadata about things stored in the app - documents, users, etc.
The actual document TEXT and embeddings live in ChromaDB; this DB just
tracks "what documents exist, when were they uploaded, how many chunks."
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# check_same_thread=False is needed for SQLite + FastAPI's threaded request handling
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once at app startup."""
    # Import models here so they're registered on Base before create_all runs
    from app.models import document  # noqa: F401

    Base.metadata.create_all(bind=engine)
