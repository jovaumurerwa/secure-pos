from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repository.sale_item_repository import sale_item_repository
from repository.sale_repository import sale_repository
from repository.product_repository import product_repository
from schemas.sale_item import SaleItemCreate, SaleItemUpdate


def get_sale_item(db: Session, id: int):
    sale_item = sale_item_repository.get(db, id)
    if not sale_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale item not found")
    return sale_item


def list_sale_items(db: Session):
    return sale_item_repository.get_all(db)


def create_sale_item(db: Session, sale_id: int, data: SaleItemCreate):
    if not sale_repository.get(db, sale_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

    payload = data.model_dump()

    if not product_repository.get(db, payload["product_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {payload['product_id']} does not exist",
        )

    return sale_item_repository.create(db, {**payload, "sale_id": sale_id})


def update_sale_item(db: Session, sale_item_id: int, data: SaleItemUpdate):
    sale_item = get_sale_item(db, sale_item_id)
    return sale_item_repository.update(db, sale_item, data.model_dump(exclude_unset=True))


def delete_sale_item(db: Session, sale_item_id: int):
    sale_item = get_sale_item(db, sale_item_id)
    sale_item_repository.delete(db, sale_item)