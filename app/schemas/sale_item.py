from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    line_discount: Decimal | None = 0
    line_total: Decimal


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    line_discount: Decimal | None = 0


class SaleItemUpdate(BaseModel):
    quantity: int | None = None
    line_discount: Decimal | None = None


class SaleItemRead(SaleItemBase):
    model_config = ConfigDict(from_attributes=True)

    sale_item_id: int
    sale_id: int