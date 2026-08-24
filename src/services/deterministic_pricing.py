"""Deterministic pricing policies for the POS core."""

from decimal import Decimal, ROUND_HALF_UP

from src.domain.contracts import Cart, DiscountPolicy, Money, PricingPolicy, VatPolicy

_CENT = Decimal("0.01")


def _money(value: Decimal, currency: str) -> Money:
    return Money(value.quantize(_CENT, rounding=ROUND_HALF_UP), currency)


class SubtotalPricingPolicy(PricingPolicy):
    def price(self, cart: Cart) -> Money:
        return cart.subtotal()


class PercentageDiscountPolicy(DiscountPolicy):
    def __init__(self, rate: Decimal) -> None:
        if rate < Decimal("0") or rate > Decimal("1"):
            raise ValueError("Discount rate must be between 0 and 1")
        self._rate = rate

    def calculate(self, cart: Cart) -> Money:
        subtotal = cart.subtotal()
        return _money(subtotal.amount * self._rate, subtotal.currency)


class VatRatePolicy(VatPolicy):
    def __init__(self, rate: Decimal) -> None:
        if rate < Decimal("0") or rate > Decimal("1"):
            raise ValueError("VAT rate must be between 0 and 1")
        self._rate = rate

    def calculate(self, subtotal: Money) -> Money:
        return _money(subtotal.amount * self._rate, subtotal.currency)
