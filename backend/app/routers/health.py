"""
Health check endpoint.

Confirms the API is running and that key config/connections are actually
working - handy for debugging a fresh deployment (wrong Supabase URL,
missing env vars, pgvector not enabled, storage bucket problems, etc.)
without digging through logs.
"""
from fastapi import APIRouter
from sqlalchemy import text as sql_text

from app.config import settings
from app.database import engine
from app.services import storage_service

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    db_connected = False
    pgvector_enabled = False
    db_error = None
    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
            db_connected = True
            result = conn.execute(
                sql_text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            ).first()
            pgvector_enabled = result is not None
    except Exception as e:
        db_error = str(e)

    storage_connected = False
    storage_error = None
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            storage_service._get_client()  # also ensures the bucket exists
            storage_connected = True
        except Exception as e:
            storage_error = str(e)

    return {
        "status": "ok",
        "gemini_api_key_loaded": bool(settings.gemini_api_key)
        and settings.gemini_api_key != "your_gemini_api_key_here",
        "supabase_storage_configured": bool(settings.supabase_url)
        and bool(settings.supabase_service_role_key),
        "supabase_storage_connected": storage_connected,
        "supabase_storage_error": storage_error,
        "database_connected": db_connected,
        "pgvector_enabled": pgvector_enabled,
        "database_error": db_error,
    }
