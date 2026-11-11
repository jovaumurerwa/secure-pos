from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["Admin", "Cashier"]

Password = Annotated[str, Field(min_length=12, max_length=128)]

Username = Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")]

FullName = Annotated[str, Field(min_length=1, max_length=150)]


class UserCreate(BaseModel):
    full_name: FullName
    username: Username
    role: Role
    email: str | None = None
    is_active: bool = True
    password: Password


class UserUpdate(BaseModel):
    full_name: FullName | None = None
    username: Username | None = None
    role: Role | None = None
    email: str | None = None
    is_active: bool | None = None
    password: Password | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    full_name: str
    username: str
    role: str
    email: str | None = None
    is_active: bool
    created_at: datetime
