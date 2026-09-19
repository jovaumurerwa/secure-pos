from models.customer import Customer
from sqlalchemy.orm import Session


class CustomerRepository:
    def __init__(self):
        self.model = Customer

    def get(self, db: Session, id: int):
        return db.get(self.model, id)

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create(self, db: Session, data: dict):
        customer = self.model(**data)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def update(self, db: Session, db_obj: Customer, data: dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Customer):
        db.delete(db_obj)
        db.commit()


customer_repository = CustomerRepository()