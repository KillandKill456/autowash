from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import require_role
from ..database import get_db
from ..models import Order, Payment, User

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
def reports(user: User = Depends(require_role("manager", "admin")),
            db: Session = Depends(get_db)):
    orders_count = db.execute(select(func.count(Order.id))).scalar() or 0
    total = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
    ).scalar() or 0
    return {"orders_count": int(orders_count), "revenue": float(total)}