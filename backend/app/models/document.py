"""
Document metadata model.

Tracks uploaded files. The actual extracted text chunks + embeddings
live in ChromaDB (see app/services/vector_store.py); this table is
just the "index card" for each document: name, status, chunk count.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime

from app.database import Base


def _new_id() -> str:
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_new_id)
    filename = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing | ready | failed
    num_chunks = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
