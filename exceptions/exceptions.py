from fastapi import HTTPException
from models import OrderStatus

class InvalidOrderIdError(HTTPException):
    """The order ID does not exist."""

    def __init__(self, order_id: int) -> None:
        super().__init__(status_code=404, detail=f"Order with id {order_id} was not found.")


class OrderAlreadyDeliveredError(HTTPException):
    """The order is already delivered, so it cannot be changed or cancelled."""

    def __init__(self, order_id: int) -> None:
        super().__init__(
            status_code=409,
            detail=f"Order {order_id} is already delivered and cannot be changed or cancelled.",
        )


class OrderAlreadyCancelledError(HTTPException):
    """The order is already cancelled."""

    def __init__(self, order_id: int) -> None:
        super().__init__(status_code=409, detail=f"Order {order_id} is already cancelled.")


class InvalidStatusTransitionError(HTTPException):
    """The requested status does not follow the order lifecycle."""

    def __init__(self, current: OrderStatus, requested: OrderStatus, allowed: set[OrderStatus]) -> None:
        allowed_text = ", ".join(s.value for s in allowed)
        super().__init__(
            status_code=409,
            detail=(
                f"Cannot change status from '{current.value}' to '{requested.value}'. "
                f"Allowed next status: {allowed_text}."
            ),
        )


class OrderNotModifiableError(HTTPException):
    """A field can no longer be edited at the order's current stage."""

    def __init__(self, order_id: int, reason: str) -> None:
        super().__init__(status_code=409, detail=f"Order {order_id} cannot be modified: {reason}.")