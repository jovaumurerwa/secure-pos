from pydantic import BaseModel, ConfigDict, EmailStr


class SupplierBase(BaseModel):
    company_name: str
    contact_name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool | None = None


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: int