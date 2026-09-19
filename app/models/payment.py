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


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False)
    payment_method = Column(String(30), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    transaction_ref = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="Approved")

    sale = relationship("Sale", back_populates="payments")