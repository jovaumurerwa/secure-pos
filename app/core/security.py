import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()  # reads .env when running locally

password_hash = PasswordHash.recommended() 


jwt_secret = os.getenv("JWT_SECRET")
if not jwt_secret or len(jwt_secret) < 32:
    raise RuntimeError("JWT_SECRET must be set in .env and be at least 32 characters.")


jwt_algorithm = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)


def decode_access_token(token: str) -> dict:
    
    return jwt.decode(
        token,
        jwt_secret,
        algorithms=[jwt_algorithm],
        options={"require": ["exp", "sub"]},
    )