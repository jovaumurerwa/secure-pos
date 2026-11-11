from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from schemas.product import ProductCreate, ProductUpdate, ProductRead
from services import product_services

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return product_services.list_products(db)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_services.get_product(db, product_id)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return product_services.create_product(db, data)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    return product_services.update_product(db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_services.delete_product(db, product_id)