from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from schemas.user import UserRead
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    return auth_service.authenticate(db, form.username, form.password)


@router.get("/me", response_model=UserRead)
def read_me(current_user=Depends(get_current_user)):
    
    return current_user