from datetime import datetime, timedelta

from ..database import SessionLocal
from ..models import Order, OrderStage, Payment


PAYMENT_DELAY_SECONDS = 15       # авто-подтверждение платежа
DONE_TTL_SECONDS = 60            # сколько живёт завершённый заказ


def process_pending_payments():
    """Переводит платежи 'pending' → 'paid' и заказ в 'paid' через 15 сек."""
    db = SessionLocal()
    try:
        now = datetime.now()
        threshold = now - timedelta(seconds=PAYMENT_DELAY_SECONDS)

        pending = (db.query(Payment)
                   .filter(Payment.status == "pending",
                           Payment.date <= threshold)
                   .all())

        for p in pending:
            p.status = "paid"
            order = db.get(Order, p.order_id)
            if order and order.status == "pending_payment":
                order.status = "paid"

        if pending:
            db.commit()
    finally:
        db.close()


def cleanup_finished_orders():
    """Удаляет заказы в статусе 'done', у которых с момента завершения
    прошло >= DONE_TTL_SECONDS секунд."""
    db = SessionLocal()
    try:
        now = datetime.now()
        threshold = now - timedelta(seconds=DONE_TTL_SECONDS)

        # находим завершённые заказы старше TTL
        done_orders = (db.query(Order)
                       .filter(Order.status == "done")
                       .all())

        to_delete = []
        for o in done_orders:
            stage = (db.query(OrderStage)
                     .filter(OrderStage.order_id == o.id,
                             OrderStage.stage == "finish")
                     .order_by(OrderStage.date.desc())
                     .first())
            if stage and stage.date and stage.date <= threshold:
                to_delete.append(o.id)

        if to_delete:
            # дочерние таблицы — с ON DELETE CASCADE обычно удаляются сами,
            # но подстрахуемся явным удалением
            (db.query(Payment)
             .filter(Payment.order_id.in_(to_delete))
             .delete(synchronize_session=False))
            (db.query(OrderStage)
             .filter(OrderStage.order_id.in_(to_delete))
             .delete(synchronize_session=False))
            (db.query(Order)
             .filter(Order.id.in_(to_delete))
             .delete(synchronize_session=False))
            db.commit()
            print(f"[scheduler] deleted finished orders: {to_delete}")
    finally:
        db.close()