from pydantic import BaseModel
from typing import Optional


class ClientBase(BaseModel):
    fullName: str
    fullSurname: str
    identified: str


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int

    class Config:
        orm_mode = True
