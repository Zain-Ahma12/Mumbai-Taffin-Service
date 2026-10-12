from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from database import get_session
from models import Order, OrderCreate, OrderStatus, OrderUpdate, StatusLog
from sqlmodel import Session, select


router = APIRouter(prefix="/orders", tags=["orders"])

@router.post(
    "/",
    response_model = Order,
    status_code = status.HTTP_201_CREATED
)
def create_order(order: OrderCreate, session: Session = Depends(get_session)) -> Order:
    db_order = Order.model_validate(order)

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    return db_order

@router.get(
    "/",
    response_model = list[Order],
    status_code = status.HTTP_200_OK
)
def list_orders(
    order_status: OrderStatus | None = Query(default=None, alias="status", description="Filter by order status"),
    created_date: str | None = Query(default=None, description="Filter by date of creation (YYYY-MM-DD)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
    session: Session = Depends(get_session)
) -> list[Order]:
    # complete this get route
    query = select(Order)

    if order_status:
        query = query.where(Order.status == order_status)

    if created_date:
        try:
            parsed_date = date.fromisoformat(created_date)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="created_date must be in YYYY-MM-DD format",
            ) from exc

        start_of_day = datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)
        next_day = start_of_day + timedelta(days=1)
        query = query.where(
            Order.created_at >= start_of_day,
            Order.created_at < next_day,
        )

    query = query.offset(skip).limit(limit)
    
    orders = session.exec(query).all()

    return orders
