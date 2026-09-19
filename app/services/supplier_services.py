from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repository.supplier_repository import supplier_repository
from schemas.supplier import SupplierCreate, SupplierUpdate


def get_supplier(db: Session, id: int):
    supplier = supplier_repository.get(db, id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


def list_suppliers(db: Session):
    return supplier_repository.get_all(db)


def create_supplier(db: Session, data: SupplierCreate):
    return supplier_repository.create(db, data.model_dump())


def update_supplier(db: Session, supplier_id: int, data: SupplierUpdate):
    supplier = get_supplier(db, supplier_id)
    return supplier_repository.update(db, supplier, data.model_dump(exclude_unset=True))


def delete_supplier(db: Session, supplier_id: int):
    supplier = get_supplier(db, supplier_id)
    supplier_repository.delete(db, supplier)