from typing import Optional
from pydantic import BaseModel


class ServiceDTO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

    model_config = {"from_attributes": True}