from models.category import Category
from sqlalchemy.orm import Session


class CategoryRepository:
    def __init__(self):
        self.model = Category

    def get(self, db: Session, id: int):
        return db.get(self.model, id)

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create(self, db: Session, data: dict):
        category = self.model(**data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def update(self, db: Session, db_obj: Category, data: dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Category):
        db.delete(db_obj)
        db.commit()


category_repository = CategoryRepository()