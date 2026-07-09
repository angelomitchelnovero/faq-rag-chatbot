"""
Application configuration.

Loads values from the .env file (see .env.example for the template).
Uses pydantic-settings so values are validated and typed.
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

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Storage paths
    upload_dir: str = "./data/uploads"
    chroma_dir: str = "./data/chroma_db"

    # CORS - frontend URL(s) allowed to call this API
    frontend_origins: list[str] = [
        "http://localhost:3000",  # Next.js dev server
    ]


# Single shared settings instance, imported elsewhere as: from app.config import settings
settings = Settings()
