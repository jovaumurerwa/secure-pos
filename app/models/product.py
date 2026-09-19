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

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String, nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
