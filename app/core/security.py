from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended() 

jwt_secret = "change-me-to-a-secret-ket-32-chars"
jwt_algorithm = "HS256"

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {'sub': str(user_id), 'exp': expire}
    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
