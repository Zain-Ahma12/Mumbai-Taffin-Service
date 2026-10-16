from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

# Order status (enum) -> preparing, picked_up, in_transit, delivered, cancled
class OrderStatus(str, Enum):
    PREPARING = "preparing"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCLED = "cancled"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_first_name: str
    customer_last_name: str
    delivery_address: str
    items: str
    status: OrderStatus = Field(default=OrderStatus.PREPARING)
    cancellation_reason: Optional[str] = None  # filled only when the order is cancelled
    created_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )

# add a table for status logs
class StatusLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    old_status: Optional[OrderStatus] = None # None when the order is first created
    new_status: OrderStatus
    reason: Optional[str] = None # only filled when the order is cancelled
    changed_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )
    

class OrderCreate(SQLModel):
    customer_first_name: str
    customer_last_name: str
    delivery_address: str
    items: str

class OrderUpdate(SQLModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None

class OrderCancel(SQLModel):
    reason: str = Field(min_length=5, max_length=255)