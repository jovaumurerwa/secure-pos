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

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    loyalty_points = Column(Integer, nullable=True, default=0)
    is_walk_in = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sales = relationship("Sale", back_populates="customer")