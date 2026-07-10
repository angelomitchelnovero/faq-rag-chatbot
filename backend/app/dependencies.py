"""
FastAPI dependencies for authentication and authorization.

Use `get_current_user` on any route that requires login.
Use `require_admin` on any route that should be admin-only.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token

# Simple "paste your token" auth scheme for Swagger UI - much simpler than
# OAuth2PasswordBearer, which expects a username/password form submission.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise unauthorized

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise unauthorized

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise unauthorized

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user
