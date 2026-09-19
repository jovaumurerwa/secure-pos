from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from services import category_services

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return category_services.list_categories(db)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_services.get_category(db, category_id)


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_services.create_category(db, data)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    return category_services.update_category(db, category_id, data)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_services.delete_category(db, category_id)