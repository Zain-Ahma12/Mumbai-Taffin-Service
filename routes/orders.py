from datetime import date, datetime, time, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from database import get_session
from models import Order, OrderCancel, OrderCreate, OrderStatus, OrderUpdate, StatusLog
from sqlmodel import Session, select
from exceptions import (
    InvalidOrderIdError,
    InvalidStatusTransitionError,
    OrderAlreadyCancelledError,
    OrderAlreadyDeliveredError,
    OrderNotModifiableError
)


router = APIRouter(prefix="/orders", tags=["orders"])

# Which status is allowed to come next
ALLOWED_TRANSITIONS : dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PREPARING: {OrderStatus.PICKED_UP},
    OrderStatus.PICKED_UP: {OrderStatus.IN_TRANSIT},
    OrderStatus.IN_TRANSIT: {OrderStatus.DELIVERED},
}


@router.post(
    "/",
    response_model = Order,
    status_code = status.HTTP_201_CREATED
)
def create_order(order: OrderCreate, session: Session = Depends(get_session)) -> Order:
    db_order = Order.model_validate(order)

    session.add(db_order)
    session.flush()  # gives db_order an id so we can log the initial status
    
    session.add(StatusLog(
        order_id=db_order.id,
        new_status=db_order.status,
        reason="Order created")
    )
    
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

@router.get(
    "/{order_id}",
    response_model = Order
)
def get_order(
    order_id: int,
    session: Session = Depends(get_session)
) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise InvalidOrderIdError(order_id)
    return order

@router.patch(
    "/{order_id}",
    response_model = Order,
)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    session: Session = Depends(get_session)
) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise InvalidOrderIdError(order_id)

    # Check if the order is already delivered or cancelled
    if order.status == OrderStatus.DELIVERED:
        raise OrderAlreadyDeliveredError(order_id)
    if order.status == OrderStatus.CANCLED:
        raise OrderAlreadyCancelledError(order_id)
    
    if order_update.status is None and order_update.delivery_address is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (status or delivery_address) must be provided for update."
        )
    
    # Checking some valid logic before saving the changes to the database
    if order_update.delivery_address is not None:
        if order.status != OrderStatus.PREPARING:
            raise OrderNotModifiableError(order_id, "Delivery address can only be changed while the order is preparing.")
        order.delivery_address = order_update.delivery_address
        
    if order_update.status is not None:
        allowed = ALLOWED_TRANSITIONS[order.status]
        if order_update.status not in allowed:
            raise InvalidStatusTransitionError(order.status, order_update.status, allowed)
    
        # Now log status and update the order
        session.add(StatusLog(
            order_id=order.id,
            old_status=order.status,
            new_status=order_update.status
        ))
        order.status = order_update.status # Update the order's status

    order.updated_at = datetime.now(timezone.utc)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.delete(
    "/{order_id}",
    response_model=Order
    )
def cancel_order(order_id: int, cancellation: OrderCancel, session: Session = Depends(get_session)) -> Order:
    
    order = session.get(Order, order_id)
    if order is None:
        raise InvalidOrderIdError(order_id)

    if order.status == OrderStatus.DELIVERED:
        raise OrderAlreadyDeliveredError(order_id)
    if order.status == OrderStatus.CANCELLED:
        raise OrderAlreadyCancelledError(order_id)

    session.add(
        StatusLog(
            order_id=order_id,
            old_status=order.status,
            new_status=OrderStatus.CANCELLED,
            reason=cancellation.reason,
        )
    )
    order.status = OrderStatus.CANCELLED
    order.cancellation_reason = cancellation.reason
    order.updated_at = datetime.now(timezone.utc)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get(
    "/{order_id}/history",
    response_model=list[StatusLog]
    )
def get_order_history(order_id: int, session: Session = Depends(get_session)) -> list[StatusLog]:
    """Get every status change of an order, oldest first."""
    order = session.get(Order, order_id)
    if order is None:
        raise InvalidOrderIdError(order_id)

    query = select(StatusLog).where(StatusLog.order_id == order_id).order_by(StatusLog.id)
    return list(session.exec(query).all())