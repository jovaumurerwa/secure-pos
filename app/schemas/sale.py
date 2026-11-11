from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .sale_item import SaleItemCreate, SaleItemRead
from .payment import PaymentCreate, PaymentRead


class SaleCreate(BaseModel):
    customer_id: int | None = None
    # No user_id here on purpose: the server takes it from the login token,
    # so a cashier can't record a sale under someone else's name.
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