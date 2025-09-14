from pydantic import BaseModel, EmailStr


class ContactsBase(BaseModel):
    phone: str
    email: EmailStr
    work_hours: str
    address: str


class ContactsCreate(ContactsBase):
    pass


class ContactsResponse(ContactsBase):
    pass


class ContactsUpdate(BaseModel):
    phone: str | None = None
    email: EmailStr | None = None
    work_hours: str | None = None
    address: str | None = None
