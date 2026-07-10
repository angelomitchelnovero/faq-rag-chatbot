"""
User model for authentication.

role is a plain string ("admin" or "user") rather than a separate table -
simple and sufficient for a two-role system like this one.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime

from app.database import Base


def _new_id() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_new_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" | "admin"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
