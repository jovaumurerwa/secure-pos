from typing import Any
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

from repository.user_repository import user_repository
from schemas.user import UserCreate

def register(db: Session, data: UserCreate):
    if user_repository.get_by_username(db=data.username):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already taken",
        )
    values = data.model_dump(exclude={'password'})
    values['hashed_password'] = hash_password(data.password)
    return user_repository.create(db, values)

def authenticate(db:Session, username: str, password: str):
    user = user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return {
        'access_token': create_access_token(user_id),
        'token_type': 'bearer'
    }
    
def get_user_from_token(db: Session, token:str):
    """Validate a JWT and return """
    credentials_code = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Invalid or expired token',
    headers={'WWW-Authenticate': 'Bearer'},
    )
    
    try:
        payload: dict[str, Any] = decode_access_token(token)
        subject = payload.get('sub')
        if not isinstance(subject, str) or not subject.strip():
            raise credentials_code
        used_id = int(subject)
        if used_id <= 0:
            raise credentials_code
        
    except Exception as e:
        raise credentials_code
    
    user = user_repository.get(db, used_id)
    if user is None:
        raise credentials_code
    if not user.is_active:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail='User account is inactive'
        )