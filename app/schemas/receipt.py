from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReceiptBase(BaseModel):
    receipt_number: str
    print_status: str = "Printed"
    copy_type: str | None = None


class ReceiptCreate(BaseModel):
    copy_type: str | None = None


class ReceiptUpdate(BaseModel):
    print_status: str | None = None
    copy_type: str | None = None


class ReceiptRead(ReceiptBase):
    model_config = ConfigDict(from_attributes=True)

    receipt_id: int
    sale_id: int
    issued_at: datetime