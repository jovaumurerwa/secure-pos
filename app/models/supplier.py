from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(150), nullable=False)
    contact_name = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    products = relationship("Product", back_populates="supplier")