from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CreateOrderDTO(BaseModel):
    car_id: Optional[int] = None
    date: date
    time: time
    service_ids: List[int] = Field(default_factory=list)


class UpdateOrderDTO(BaseModel):
    service_ids: List[int]


class OrderDTO(BaseModel):
    id: int
    user_id: int
    car_id: Optional[int] = None
    date: date
    time: time
    status: str
    finished_at: Optional[datetime] = None
    total: float = 0.0
    client_name: Optional[str] = None
    client_phone: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderPriceDTO(BaseModel):
    order_id: int
    total: float


class PaymentDTO(BaseModel):
    payment_id: int
    amount: float
    pay_url: Optional[str] = None
    status: Optional[str] = None


class ReviewDTO(BaseModel):
    rating: int
    text: Optional[str] = None


class StageDTO(BaseModel):
    stage: str