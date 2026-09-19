from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerRead
from services import customer_services

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    return customer_services.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return customer_services.get_customer(db, customer_id)


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_services.create_customer(db, data)


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    return customer_services.update_customer(db, customer_id, data)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer_services.delete_customer(db, customer_id)