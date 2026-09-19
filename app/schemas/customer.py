from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    full_name: str
    phone: str | None = None
    email: str | None = None
    loyalty_points: int | None = 0
    is_walk_in: bool = False


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    loyalty_points: int | None = None
    is_walk_in: bool | None = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    created_at: datetime