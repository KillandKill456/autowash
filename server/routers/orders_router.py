from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..dto.order_dto import (CreateOrderDTO, OrderDTO, OrderPriceDTO,
                             PaymentDTO, ReviewDTO, UpdateOrderDTO)
from ..models import User
from ..services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderDTO, status_code=201)
def create_order(dto: CreateOrderDTO,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return OrderService(db).create(user, dto)


@router.get("", response_model=list[OrderDTO])
def list_orders(user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return OrderService(db).list_for(user)


@router.get("/{order_id}", response_model=OrderDTO)
def get_order(order_id: int,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).get(order_id, user)


@router.get("/{order_id}/price", response_model=OrderPriceDTO)
def get_price(order_id: int,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).price(order_id, user)


@router.patch("/{order_id}", response_model=OrderDTO)
def update_order(order_id: int, dto: UpdateOrderDTO,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return OrderService(db).update_services(order_id, dto.service_ids, user)


@router.post("/{order_id}/check")
def check_order(order_id: int,
                user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return OrderService(db).check_feasibility(order_id, user)


@router.post("/{order_id}/payment", response_model=PaymentDTO)
def create_payment(order_id: int,
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return OrderService(db).create_payment(order_id, user)


@router.get("/{order_id}/payment", response_model=PaymentDTO)
def payment_status(order_id: int,
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return OrderService(db).payment_status(order_id, user)


@router.patch("/{order_id}/stages")
def add_stage(order_id: int, stage: str,
              _body: dict = Body(default={}),
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).add_stage(order_id, stage, user)


@router.post("/{order_id}/review", status_code=201)
def leave_review(order_id: int, dto: ReviewDTO,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return OrderService(db).leave_review(order_id, dto, user)


@router.delete("/{order_id}")
def delete_order(order_id: int,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return OrderService(db).delete(order_id, user)