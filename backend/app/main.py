"""
FastAPI entrypoint for the FAQ RAG Chatbot backend.

Run locally with:
    uvicorn app.main:app --reload

Interactive docs available at:
    http://localhost:8000/docs
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import health, documents, chat

app = FastAPI(
    title="FAQ RAG Chatbot API",
    description="Backend for a RAG-based FAQ chatbot with admin and user interfaces.",
    version="0.1.0",
)

# Allow the Next.js frontend (running on a different port/domain) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Make sure the folders we depend on actually exist before anything tries to use them
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_dir, exist_ok=True)
    init_db()


@app.get("/")
def read_root():
    return {"status": "ok", "message": "FAQ RAG Chatbot API is running"}


# Routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
