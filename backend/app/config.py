"""
Application configuration.

Loads values from the .env file (see .env.example for the template).
Uses pydantic-settings so values are validated and typed.

Note: this app is designed to be stateless - all persistent data (users,
documents, vector embeddings, uploaded/generated PDFs) lives in Supabase
(Postgres with pgvector, and Supabase Storage), not on local disk. This
means it's safe to run on hosts with ephemeral disks (e.g. Render's free
tier) without losing data on every restart/redeploy.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Gemini
    gemini_api_key: str = ""

    # Auth
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours

    # Secret code required to register as an admin (prevents open admin signup)
    admin_signup_code: str = "change-this-admin-code"

    # Database - a Postgres connection string (Supabase provides one; see
    # .env.example for where to find it). Must be Postgres, not SQLite -
    # the vector_store module uses the pgvector extension.
    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # Supabase Storage (holds the PDFs - original uploads and any
    # admin-edited/regenerated versions)
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "documents"

    # CORS - frontend URL(s) allowed to call this API
    frontend_origins: list[str] = [
        "http://localhost:3000",  # Next.js dev server
    ]


# Single shared settings instance, imported elsewhere as: from app.config import settings
settings = Settings()
