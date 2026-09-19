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


class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), unique=True, nullable=False)
    receipt_number = Column(String(30), unique=True, nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    print_status = Column(String(20), nullable=False, default="Printed")
    copy_type = Column(String(20), nullable=True)

    sale = relationship("Sale", back_populates="receipt")