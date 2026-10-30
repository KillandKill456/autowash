from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from ..dto.order_dto import (CreateOrderDTO, OrderDTO, OrderPriceDTO,
                             PaymentDTO, ReviewDTO)
from ..models import (Order, OrderServiceItem, Service, Payment,
                      OrderStage, Review, User)


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def _calc_total(self, order_id: int) -> float:
        rows = self.db.execute(
            select(OrderServiceItem)
            .where(OrderServiceItem.order_id == order_id)
        ).scalars().all()
        return float(sum(r.price * r.quantity for r in rows))

    def _fill_client(self, dto: OrderDTO, order: Order):
        client = self.db.get(User, order.user_id)
        if client:
            dto.client_name = client.name
            dto.client_phone = client.phone

    def _get_owned(self, order_id: int, user: User) -> Order:
        order = self.db.get(Order, order_id)
        if not order:
            raise HTTPException(404, "Заказ не найден")
        if user.role == "client" and order.user_id != user.id:
            raise HTTPException(403, "Нет доступа к заказу")
        return order

    def create(self, user: User, dto: CreateOrderDTO) -> OrderDTO:
        if user.role == "admin":
            raise HTTPException(403, "Администратор не создаёт заказы")
        try:
            order = Order(user_id=user.id, car_id=dto.car_id,
                          date=dto.date, time=dto.time, status="draft")
            self.db.add(order)
            self.db.flush()

            for sid in dto.service_ids:
                svc = self.db.get(Service, sid)
                if not svc:
                    raise HTTPException(400, f"Услуга {sid} не найдена")
                self.db.add(OrderServiceItem(order_id=order.id,
                                             service_id=sid,
                                             quantity=1, price=svc.price))

            self.db.commit()
            self.db.refresh(order)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка создания заказа")

        out = OrderDTO.model_validate(order)
        out.total = self._calc_total(order.id)
        self._fill_client(out, order)
        return out

    def list_for(self, user: User) -> list[OrderDTO]:
        stmt = select(Order)
        if user.role == "client":
            stmt = stmt.where(Order.user_id == user.id)
        elif user.role == "washer":
            stmt = stmt.where(Order.status.in_(["paid", "in_progress"]))

        orders = self.db.execute(stmt).scalars().all()
        result = []
        for o in orders:
            dto = OrderDTO.model_validate(o)
            if o.status == "done":
                stage = self.db.execute(
                    select(OrderStage)
                    .where(OrderStage.order_id == o.id,
                           OrderStage.stage == "finish")
                    .order_by(OrderStage.date.desc())
                ).scalars().first()
                if stage:
                    dto.finished_at = stage.date
            dto.total = self._calc_total(o.id)
            self._fill_client(dto, o)
            result.append(dto)
        return result

    def get(self, order_id: int, user: User) -> OrderDTO:
        order = self._get_owned(order_id, user)
        dto = OrderDTO.model_validate(order)
        dto.total = self._calc_total(order_id)
        self._fill_client(dto, order)
        return dto

    def price(self, order_id: int, user: User) -> OrderPriceDTO:
        self._get_owned(order_id, user)
        return OrderPriceDTO(order_id=order_id,
                             total=self._calc_total(order_id))

    def update_services(self, order_id: int, service_ids: list[int],
                        user: User) -> OrderDTO:
        order = self._get_owned(order_id, user)
        if order.status not in ("draft", "pending_payment"):
            raise HTTPException(409, "Заказ уже нельзя менять")
        try:
            self.db.execute(
                delete(OrderServiceItem)
                .where(OrderServiceItem.order_id == order_id)
            )
            for sid in service_ids:
                svc = self.db.get(Service, sid)
                if not svc:
                    raise HTTPException(400, f"Услуга {sid} не найдена")
                self.db.add(OrderServiceItem(order_id=order.id,
                                             service_id=sid,
                                             quantity=1, price=svc.price))
            self.db.commit()
            self.db.refresh(order)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка обновления заказа")

        out = OrderDTO.model_validate(order)
        out.total = self._calc_total(order.id)
        self._fill_client(out, order)
        return out

    def check_feasibility(self, order_id: int, user: User) -> dict:
        order = self._get_owned(order_id, user)
        return {"feasible": True, "order_id": order.id}

    def create_payment(self, order_id: int, user: User) -> PaymentDTO:
        if user.role == "admin":
            raise HTTPException(403, "Администратор не оплачивает заказы")
        order = self._get_owned(order_id, user)
        try:
            total = self._calc_total(order_id)
            payment = Payment(order_id=order.id, amount=total,
                              status="pending")
            self.db.add(payment)
            order.status = "pending_payment"
            self.db.commit()
            self.db.refresh(payment)
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка платежа")
        return PaymentDTO(payment_id=payment.id, amount=float(total),
                          pay_url=f"https://bank.example/pay/{payment.id}",
                          status=payment.status)

    def payment_status(self, order_id: int, user: User) -> PaymentDTO:
        self._get_owned(order_id, user)
        p = self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
            .order_by(Payment.id.desc())
        ).scalars().first()
        if not p:
            raise HTTPException(404, "Платёж не найден")
        return PaymentDTO(payment_id=p.id, amount=float(p.amount),
                          status=p.status)

    def add_stage(self, order_id: int, stage: str, user: User) -> dict:
        order = self.db.get(Order, order_id)
        if not order:
            raise HTTPException(404, "Заказ не найден")
        if user.role not in ("washer", "manager", "admin"):
            raise HTTPException(403, "Недостаточно прав")
        try:
            self.db.add(OrderStage(order_id=order_id, washer_id=user.id,
                                   stage=stage))
            if stage == "start":
                order.status = "in_progress"
            elif stage == "finish":
                order.status = "done"
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка смены этапа")
        return {"ok": True, "order_status": order.status}

    def leave_review(self, order_id: int, dto: ReviewDTO, user: User) -> dict:
        self._get_owned(order_id, user)
        existing = self.db.execute(
            select(Review).where(Review.order_id == order_id)
        ).scalars().first()
        if existing:
            raise HTTPException(409, "Отзыв уже оставлен")
        try:
            self.db.add(Review(order_id=order_id, rating=dto.rating,
                               text=dto.text, author_id=user.id))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка сохранения отзыва")
        return {"ok": True}

    def delete(self, order_id: int, user: User) -> dict:
        if user.role != "admin":
            raise HTTPException(403, "Только администратор может удалять")
        order = self.db.get(Order, order_id)
        if not order:
            raise HTTPException(404, "Заказ не найден")
        try:
            self.db.execute(
                delete(OrderServiceItem)
                .where(OrderServiceItem.order_id == order_id)
            )
            self.db.execute(
                delete(OrderStage)
                .where(OrderStage.order_id == order_id)
            )
            self.db.execute(
                delete(Payment)
                .where(Payment.order_id == order_id)
            )
            self.db.execute(
                delete(Review)
                .where(Review.order_id == order_id)
            )
            self.db.delete(order)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка удаления заказа")
        return {"ok": True, "deleted_order_id": order_id}