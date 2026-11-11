from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core import rate_limit
from database import get_db
from dependencies import get_current_user
from schemas.user import UserRead
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Count failures per IP address AND username, so one attacker can't lock out everyone
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{form.username.lower()}"

    wait = rate_limit.seconds_until_allowed(key)
    if wait:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again later.",
            headers={"Retry-After": str(wait)},
        )

    try:
        token = auth_service.authenticate(db, form.username, form.password)
    except HTTPException as error:
        if error.status_code == status.HTTP_401_UNAUTHORIZED:
            rate_limit.record_failure(key)  # only wrong passwords count
        raise

    rate_limit.clear(key)
    return token


@router.get("/me", response_model=UserRead)
def read_me(current_user=Depends(get_current_user)):
    # Returns whoever owns the token. The frontend uses this to show "Logged in as ..." and pick screens by role
    return current_user
