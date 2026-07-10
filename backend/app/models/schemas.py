"""
Pydantic schemas (API request/response shapes) for documents.

Kept separate from app/models/document.py, which is the SQLAlchemy
DB model. This file defines what the API actually sends/receives over HTTP.
"""
from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    num_chunks: int
    error_message: str | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object directly


class ChatRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    filename: str
    text: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
