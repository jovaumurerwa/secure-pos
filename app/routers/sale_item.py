from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.sale_item import SaleItemCreate, SaleItemUpdate, SaleItemRead
from services import sale_item_services

router = APIRouter(prefix="/sale-items", tags=["Sale Items"])


@router.get("/", response_model=list[SaleItemRead])
def list_sale_items(db: Session = Depends(get_db)):
    return sale_item_services.list_sale_items(db)


@router.get("/{sale_item_id}", response_model=SaleItemRead)
def get_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    return sale_item_services.get_sale_item(db, sale_item_id)


@router.post("/sale/{sale_id}", response_model=SaleItemRead, status_code=status.HTTP_201_CREATED)
def create_sale_item(sale_id: int, data: SaleItemCreate, db: Session = Depends(get_db)):
    return sale_item_services.create_sale_item(db, sale_id, data)


@router.put("/{sale_item_id}", response_model=SaleItemRead)
def update_sale_item(sale_item_id: int, data: SaleItemUpdate, db: Session = Depends(get_db)):
    return sale_item_services.update_sale_item(db, sale_item_id, data)


@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    sale_item_services.delete_sale_item(db, sale_item_id)