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
):
    if summary_date is None:
        summary_date = date.today()
        start_of_day = datetime.combine(summary_date, time.min, tzinfo=timezone.utc)
        next_day = start_of_day + timedelta(days=1)

    summary = {}
    total = 0
    
    for status in OrderStatus:
        count = session.exec(
            select(func.count(Order.id))
            .where(
                Order.created_at >= start_of_day,
                Order.created_at < next_day,
                Order.status == status
            )
        ).one()
        summary[status.value] = count # Store the count for each status in the summary dictionary
        total += count # Add the count to the total
    return {
        "summary_date": summary_date.isoformat(),
        "summary": summary,
        "total_orders": total
    }