from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repository.product_repository import product_repository
from repository.category_repository import category_repository
from repository.supplier_repository import supplier_repository
from schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, id: int):
    product = product_repository.get(db, id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def list_products(db: Session):
    return product_repository.get_all(db)


def create_product(db: Session, data: ProductCreate):
    payload = data.model_dump()

    if not category_repository.get(db, payload["category_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category {payload['category_id']} does not exist",
        )

    if payload.get("supplier_id") is not None:
        if not supplier_repository.get(db, payload["supplier_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supplier {payload['supplier_id']} does not exist",
            )

    return product_repository.create(db, payload)


def update_product(db: Session, product_id: int, data: ProductUpdate):
    product = get_product(db, product_id)
    update_data = data.model_dump(exclude_unset=True)

    if "category_id" in update_data and not category_repository.get(db, update_data["category_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")

    if "supplier_id" in update_data and update_data["supplier_id"] is not None:
        if not supplier_repository.get(db, update_data["supplier_id"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier does not exist")

    return product_repository.update(db, product, update_data)


def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    product_repository.delete(db, product)