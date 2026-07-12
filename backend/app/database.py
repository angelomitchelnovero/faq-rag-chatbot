"""
Database setup - Supabase Postgres.

Tracks metadata about things stored in the app - documents, users, and
(via vector_store.DocumentChunk) the chunk embeddings themselves, using
the pgvector extension. Everything lives in Postgres so there's a single
source of truth shared between local dev and the deployed backend.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

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
    """Enable pgvector and create all tables. Called once at app startup."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Import models here so they're registered on Base before create_all runs
    from app.models import document, user  # noqa: F401
    from app.services import vector_store  # noqa: F401 - registers DocumentChunk table

    Base.metadata.create_all(bind=engine)
