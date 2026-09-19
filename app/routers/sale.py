from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.sale import SaleCreate, SaleUpdate, SaleRead
from services import sale_services

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/", response_model=list[SaleRead])
def list_sales(db: Session = Depends(get_db)):
    return sale_services.list_sales(db)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    return sale_services.get_sale(db, sale_id)


@router.post("/", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_sale(data: SaleCreate, db: Session = Depends(get_db)):
    return sale_services.create_sale(db, data)


@router.put("/{sale_id}", response_model=SaleRead)
def update_sale(sale_id: int, data: SaleUpdate, db: Session = Depends(get_db)):
    return sale_services.update_sale(db, sale_id, data)


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    sale_services.delete_sale(db, sale_id)