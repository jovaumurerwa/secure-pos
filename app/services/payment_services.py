from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repository.payment_repository import payment_repository
from repository.sale_repository import sale_repository
from schemas.payment import PaymentCreate, PaymentUpdate


def get_payment(db: Session, id: int):
    payment = payment_repository.get(db, id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


def list_payments(db: Session):
    return payment_repository.get_all(db)


def create_payment(db: Session, sale_id: int, data: PaymentCreate):
    if not sale_repository.get(db, sale_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

    payment_data = data.model_dump()
    payment_data["sale_id"] = sale_id
    payment_data["status"] = "Approved"
    return payment_repository.create(db, payment_data)


def update_payment(db: Session, payment_id: int, data: PaymentUpdate):
    payment = get_payment(db, payment_id)
    return payment_repository.update(db, payment, data.model_dump(exclude_unset=True))


def delete_payment(db: Session, payment_id: int):
    payment = get_payment(db, payment_id)
    payment_repository.delete(db, payment)