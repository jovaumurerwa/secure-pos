from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .sale_item import SaleItemCreate, SaleItemRead
from .payment import PaymentCreate, PaymentRead


class SaleCreate(BaseModel):
    customer_id: int | None = None
    user_id: int
    discount_amount: Decimal | None = 0
    sale_items: list[SaleItemCreate]
    payments: list[PaymentCreate]


class SaleUpdate(BaseModel):
    customer_id: int | None = None
    status: str | None = None


class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_id: int
    sale_number: str
    customer_id: int | None
    user_id: int
    sale_date: datetime
    subtotal: Decimal
    discount_amount: Decimal | None
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    sale_items: list[SaleItemRead] = []
    payments: list[PaymentRead] = []