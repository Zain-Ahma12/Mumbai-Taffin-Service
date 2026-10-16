from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func
from database import get_session
from datetime import datetime,  date, time, timedelta, timezone
from models import Order, OrderStatus


router = APIRouter(prefix="/stats", tags=["stats"])

@router.get(
    "/daily",
    status_code = status.HTTP_200_OK
)
def daily_summary(
    summary_date: date | None = Query(default=None, description="date for summary (YYYY-MM-DD)"),
    session: Session = Depends(get_session)
) -> dict[str, object]:
    day = summary_date or datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(day, time.min, tzinfo=timezone.utc)
    next_day = start_of_day + timedelta(days=1)
    
    # querry that counts orders per status.
    rows = session.exec(
        select(Order.status, func.count(Order.id))
        .where(
            Order.created_at >= start_of_day,
            Order.created_at < next_day
        )
        .group_by(Order.status)
    ).all()


    # Start every status at 0 so the response always has the same shape.
    by_status = {s.value: 0 for s in OrderStatus}
    for order_status, count in rows:
        by_status[order_status.value] = count
    
    total = sum(by_status.values())
    delivered = by_status[OrderStatus.DELIVERED.value]
    cancelled = by_status[OrderStatus.CANCLED.value]

    return {
        "summary_date": day.isoformat(),
        "total_orders": total,
        "by_status": by_status,
        "active_orders": total - delivered - cancelled, # still preparing or on the way
        "delivery_rate_percent": round(delivered / total * 100, 2) if total  else 0,
        "cancellation_rate_percent": round(cancelled / total * 100, 2) if total else 0,
    }