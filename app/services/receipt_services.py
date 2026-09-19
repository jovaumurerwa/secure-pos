from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.receipt import Receipt
from repository.receipt_repository import receipt_repository
from repository.sale_repository import sale_repository
from schemas.receipt import ReceiptCreate, ReceiptUpdate


def get_receipt(db: Session, id: int):
    receipt = receipt_repository.get(db, id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    return receipt


def list_receipts(db: Session):
    return receipt_repository.get_all(db)


def issue_receipt(db: Session, sale_id: int, data: ReceiptCreate):
    sale = sale_repository.get(db, sale_id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    receipt_number = sale.sale_number.replace("SALE-", "RCPT-")

    receipt = Receipt(
        sale_id=sale.sale_id,
        receipt_number=receipt_number,
        print_status="Printed",
        copy_type=data.copy_type,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def update_receipt(db: Session, receipt_id: int, data: ReceiptUpdate):
    receipt = get_receipt(db, receipt_id)
    return receipt_repository.update(db, receipt, data.model_dump(exclude_unset=True))