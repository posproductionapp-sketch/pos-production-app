"""Stable domain contracts for the POS core.

The domain layer is deterministic and infrastructure-agnostic.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "THB"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Money amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")


@dataclass(frozen=True)
class LineItem:
    product_id: str
    quantity: Decimal
    unit_price: Money

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ValueError("Product id is required")
        if self.quantity <= Decimal("0"):
            raise ValueError("Quantity must be greater than zero")


@dataclass(frozen=True)
class Cart:
    items: tuple[LineItem, ...]

    def __post_init__(self) -> None:
        currencies = {item.unit_price.currency for item in self.items}
        if len(currencies) > 1:
            raise ValueError("Cart items must use one currency")

    def subtotal(self) -> Money:
        if not self.items:
            return Money(Decimal("0"))
        currency = self.items[0].unit_price.currency
        total = sum(
            (item.unit_price.amount * item.quantity for item in self.items),
            Decimal("0"),
        )
        return Money(total, currency)


class PricingPolicy(Protocol):
    def price(self, cart: Cart) -> Money:
        """Return the deterministic price for a cart."""


class VatPolicy(Protocol):
    def calculate(self, subtotal: Money) -> Money:
        """Calculate VAT deterministically."""


class DiscountPolicy(Protocol):
    def calculate(self, cart: Cart) -> Money:
        """Calculate discounts deterministically."""
