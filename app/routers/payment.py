from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.payment import PaymentCreate, PaymentUpdate, PaymentRead
from services import payment_services

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=list[PaymentRead])
def list_payments(db: Session = Depends(get_db)):
    return payment_services.list_payments(db)


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_services.get_payment(db, payment_id)


@router.post("/sale/{sale_id}", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(sale_id: int, data: PaymentCreate, db: Session = Depends(get_db)):
    return payment_services.create_payment(db, sale_id, data)


@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment(payment_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    return payment_services.update_payment(db, payment_id, data)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment_services.delete_payment(db, payment_id)