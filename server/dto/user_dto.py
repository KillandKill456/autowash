from typing import Optional
from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    password: str


class UserDTO(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str] = None
    role: str

    model_config = {"from_attributes": True}