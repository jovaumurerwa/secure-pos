from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.receipt import ReceiptCreate, ReceiptUpdate, ReceiptRead
from services import receipt_services

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.get("/", response_model=list[ReceiptRead])
def list_receipts(db: Session = Depends(get_db)):
    return receipt_services.list_receipts(db)


@router.get("/{receipt_id}", response_model=ReceiptRead)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    return receipt_services.get_receipt(db, receipt_id)


@router.post("/sale/{sale_id}", response_model=ReceiptRead, status_code=status.HTTP_201_CREATED)
def issue_receipt(sale_id: int, data: ReceiptCreate, db: Session = Depends(get_db)):
    return receipt_services.issue_receipt(db, sale_id, data)


@router.put("/{receipt_id}", response_model=ReceiptRead)
def update_receipt(receipt_id: int, data: ReceiptUpdate, db: Session = Depends(get_db)):
    return receipt_services.update_receipt(db, receipt_id, data)