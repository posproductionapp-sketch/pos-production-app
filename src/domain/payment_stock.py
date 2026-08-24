"""Payment and stock domain contracts."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from src.domain.contracts import Money


@dataclass(frozen=True)
class Payment:
    payment_id: str
    amount: Money
    method: str

    def __post_init__(self) -> None:
        if not self.payment_id or not self.method:
            raise ValueError("Payment id and method are required")


@dataclass(frozen=True)
class StockReservation:
    product_id: str
    quantity: Decimal

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ValueError("Product id is required")
        if self.quantity <= Decimal("0"):
            raise ValueError("Reservation quantity must be greater than zero")


class PaymentPort(Protocol):
    def authorize(self, payment: Payment) -> bool:
        """Authorize a payment through an injected adapter."""


class StockPort(Protocol):
    def reserve(self, reservation: StockReservation) -> bool:
        """Reserve stock through an injected adapter."""

    def release(self, reservation: StockReservation) -> bool:
        """Release a previous stock reservation."""
