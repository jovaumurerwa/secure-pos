from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    sku: str
    name: str
    description: str | None = None
    unit_price: Decimal
    cost_price: Decimal | None = None
    quantity_in_stock: int = 0
    reorder_level: int | None = None
    category_id: int
    supplier_id: int | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    unit_price: Decimal | None = None
    cost_price: Decimal | None = None
    quantity_in_stock: int | None = None
    reorder_level: int | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    created_at: datetime