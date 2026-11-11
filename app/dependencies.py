from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from services.auth_service import get_user_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ADMIN = "Admin"
CASHIER = "Cashier"


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return get_user_from_token(db, token)


def cashier_can(*methods: str):
    """
    Build a role check for a whole router.
    Admins can do everything. Cashiers can only use the HTTP methods listed.
    Example: cashier_can("GET") -> cashiers can read but not create, edit or delete.
    """
    allowed_for_cashier = set(methods)

    def check(request: Request, user=Depends(get_current_user)):
        if user.role == ADMIN:
            return user
        if user.role == CASHIER and request.method in allowed_for_cashier:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to do this")

    return check
