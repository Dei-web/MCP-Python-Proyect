from pydantic import BaseModel
from typing import Optional


class ClientContactBase(BaseModel):
    phoneNumber: str
    email: str
    address: Optional[str] = None


class ClientContactCreate(ClientContactBase):
    clientId: int


class ClientContactResponse(ClientContactBase):
    id: int

    class Config:
        orm_mode = True
