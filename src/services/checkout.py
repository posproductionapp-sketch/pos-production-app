"""Deterministic checkout application service.

This service composes domain pricing policies without depending on persistence,
HTTP, AI, or vendor SDKs.
"""

from src.app.contracts import CheckoutRequest, CheckoutResult
from src.domain.contracts import DiscountPolicy, Money, PricingPolicy, VatPolicy


class CheckoutService:
    """Calculate a deterministic checkout quote from explicit domain policies."""

    def __init__(
        self,
        pricing: PricingPolicy,
        discount: DiscountPolicy,
        vat: VatPolicy,
    ) -> None:
        self._pricing = pricing
        self._discount = discount
        self._vat = vat

    def quote(self, request: CheckoutRequest) -> CheckoutResult:
        subtotal = self._pricing.price(request.cart)
        discount = self._discount.calculate(request.cart)

        if discount.currency != subtotal.currency:
            raise ValueError("Discount currency must match subtotal currency")
        if discount.amount > subtotal.amount:
            raise ValueError("Discount cannot exceed subtotal")

        taxable = Money(subtotal.amount - discount.amount, subtotal.currency)
        vat = self._vat.calculate(taxable)

        if vat.currency != taxable.currency:
            raise ValueError("VAT currency must match taxable amount currency")
        if vat.amount < 0:
            raise ValueError("VAT cannot be negative")

        total = Money(taxable.amount + vat.amount, taxable.currency)
        return CheckoutResult(subtotal, discount, vat, total)
