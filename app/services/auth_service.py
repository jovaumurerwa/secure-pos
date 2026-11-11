from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token, decode_access_token, hash_password, verify_password
from repository.user_repository import user_repository


_DUMMY_HASH = hash_password("dummy-password-for-timing-only")


def authenticate(db: Session, username: str, password: str) -> dict:
    """Check username + password and return a JWT access token."""
    login_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = user_repository.get_by_username(db, username)
    if user is None:
        verify_password(password, _DUMMY_HASH)
        raise login_error
    if not verify_password(password, user.password_hash):
        raise login_error
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    return {"access_token": create_access_token(user.user_id), "token_type": "bearer"}


def get_user_from_token(db: Session, token: str):
    """Decode a JWT and return the matching active user, or raise 401/403."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict[str, Any] = decode_access_token(token)
        user_id = int(payload.get("sub", ""))
    except Exception:
        raise credentials_error

    user = user_repository.get(db, user_id)
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    return user  