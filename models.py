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
    created_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )
    

class OrderCreate(SQLModel):
    customer_first_name: str
    customer_last_name: str
    items: str

class OrderUpdateStatus(SQLModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None

class StatusLog(SQLModel):
    order_id: int
    old_status: OrderStatus
    new_status: OrderStatus
    changed_at: datetime