from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    full_name: str
    username: str
    role: str
    email: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None
    role: str | None = None
    email: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    created_at: datetime