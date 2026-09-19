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

class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    sale_number = Column(String(30), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=True, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="Completed")

    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sale")
    payments = relationship("Payment", back_populates="sale")
    receipt = relationship("Receipt", back_populates="sale", uselist=False)