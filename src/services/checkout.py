"""Deterministic checkout application service.

This service composes domain pricing policies without depending on persistence,
HTTP, AI, or vendor SDKs.
"""

from dataclasses import dataclass

from src.app.contracts import CheckoutRequest, CheckoutResult
from src.domain.contracts import Money


class CheckoutService:
    """Calculate a deterministic checkout quote from explicit domain policies."""

    def __init__(self, pricing, discount, vat) -> None:
        self._pricing = pricing
        self._discount = discount
        self._vat = vat

    def quote(self, request: CheckoutRequest) -> CheckoutResult:
        subtotal = self._pricing.price(request.cart)
        discount = self._discount.calculate(request.cart)
        taxable = Money(subtotal.amount - discount.amount, subtotal.currency)
        if taxable.amount < 0:
            raise ValueError("Discount cannot exceed subtotal")
        vat = self._vat.calculate(taxable)
        total = Money(taxable.amount + vat.amount, taxable.currency)
        return CheckoutResult(subtotal, discount, vat, total)
