"""Order lifecycle and refund invariants."""

from dataclasses import dataclass
from enum import StrEnum

from src.domain.contracts import Money


class OrderState(StrEnum):
    PENDING = "pending"
    STOCK_RESERVED = "stock_reserved"
    PAID = "paid"
    COMPLETED = "completed"
    REFUND_PENDING = "refund_pending"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


_ALLOWED = {
    OrderState.PENDING: {OrderState.STOCK_RESERVED, OrderState.CANCELLED},
    OrderState.STOCK_RESERVED: {OrderState.PAID, OrderState.CANCELLED},
    OrderState.PAID: {OrderState.COMPLETED, OrderState.REFUND_PENDING},
    OrderState.COMPLETED: {OrderState.REFUND_PENDING},
    OrderState.REFUND_PENDING: {OrderState.REFUNDED},
    OrderState.REFUNDED: set(),
    OrderState.CANCELLED: set(),
}


@dataclass(frozen=True)
class Order:
    order_id: str
    total: Money
    state: OrderState = OrderState.PENDING

    def transition(self, target: OrderState) -> "Order":
        if target not in _ALLOWED[self.state]:
            raise ValueError(f"Invalid order transition: {self.state} -> {target}")
        return Order(self.order_id, self.total, target)


@dataclass(frozen=True)
class Refund:
    refund_id: str
    order_id: str
    amount: Money

    def __post_init__(self) -> None:
        if not self.refund_id or not self.order_id:
            raise ValueError("Refund and order ids are required")
        if self.amount.amount <= 0:
            raise ValueError("Refund amount must be greater than zero")
