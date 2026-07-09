"""
Health check endpoint.

Useful for confirming the API is running, and that key config
(Gemini key, storage folders) is properly loaded — handy for
debugging local setup issues before we build the real features.
"""
import os
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "gemini_api_key_loaded": bool(settings.gemini_api_key)
        and settings.gemini_api_key != "your_gemini_api_key_here",
        "upload_dir_exists": os.path.isdir(settings.upload_dir),
        "chroma_dir_exists": os.path.isdir(settings.chroma_dir),
    }
