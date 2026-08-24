"""Application-layer data contracts and service ports.

Application code coordinates domain policies and ports; concrete business
implementations belong in the services layer.
"""

from dataclasses import dataclass
from typing import Protocol

from src.domain.contracts import Cart, Money


@dataclass(frozen=True)
class CheckoutRequest:
    cart: Cart


@dataclass(frozen=True)
class CheckoutResult:
    subtotal: Money
    discount: Money
    vat: Money
    total: Money


@dataclass(frozen=True)
class PaymentRequest:
    amount: Money
    reference: str


@dataclass(frozen=True)
class PaymentResult:
    approved: bool
    reference: str
    amount: Money


class CheckoutServicePort(Protocol):
    """Port consumed by checkout orchestration."""

    def quote(self, request: CheckoutRequest) -> CheckoutResult:
        """Produce a deterministic checkout quote."""
