from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    payment_method: str
    amount: Decimal
    transaction_ref: str | None = None
    status: str = "Approved"


class PaymentCreate(BaseModel):
    payment_method: str
    amount: Decimal
    transaction_ref: str | None = None


class PaymentUpdate(BaseModel):
    status: str | None = None
    transaction_ref: str | None = None


class PaymentRead(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    sale_id: int
    payment_date: datetime