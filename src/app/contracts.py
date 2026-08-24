"""Application-layer contracts.

Application code coordinates domain policies and ports; it does not own
vendor SDKs or persistence implementations.
"""

from dataclasses import dataclass
from decimal import Decimal

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


class CheckoutService:
    """Orchestrates deterministic checkout policies.

    Concrete implementations belong in the application/services layer and
    receive explicit domain policies through dependency injection.
    """

    def __init__(self, pricing, discount, vat) -> None:
        self._pricing = pricing
        self._discount = discount
        self._vat = vat

    def quote(self, request: CheckoutRequest) -> CheckoutResult:
        subtotal = request.cart.subtotal()
        discount = self._discount.calculate(request.cart)
        taxable = Money(subtotal.amount - discount.amount, subtotal.currency)
        vat = self._vat.calculate(taxable)
        total = Money(taxable.amount + vat.amount, taxable.currency)
        return CheckoutResult(subtotal, discount, vat, total)
