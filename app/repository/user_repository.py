from typing import List, Optional, Any
from models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import select


class UserRepository:
    def __init__(self):
        self.model = User

    def get(self, db: Session, id: int) -> Optional[User]:
        """Fetch a single user by their primary key ID."""
        return db.get(self.model, id)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Fetch a single user by their unique username."""
        return db.query(self.model).filter(self.model.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Fetch a single user by their unique email address."""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_attributes(self, db: Session, **kwargs: Any) -> Optional[User]:
        """
        Dynamically fetch a user by any keyword argument criteria.
        Example: repo.get_by_attributes(db, phone="12345", is_active=True)
        """
        return db.query(self.model).filter_by(**kwargs).first()

    def get_all(self, db: Session) -> List[User]:
        """Fetch all users from the database."""
        return db.query(self.model).all()

    def create(self, db: Session, data: dict) -> User:
        """Create and commit a new user record."""
        user = self.model(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, db_obj: User, data: dict) -> User:
        """Update fields on an existing user object."""
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: User) -> None:
        """Remove a user from the database."""
        db.delete(db_obj)
        db.commit()


user_repository = UserRepository()
