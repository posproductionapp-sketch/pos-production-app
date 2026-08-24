from decimal import Decimal

from src.domain.contracts import Cart, LineItem, Money
from src.services.deterministic_pricing import (
    PercentageDiscountPolicy,
    SubtotalPricingPolicy,
    VatRatePolicy,
)


def cart() -> Cart:
    return Cart((LineItem("coffee", Decimal("2"), Money(Decimal("50"))),))


def test_subtotal_policy() -> None:
    assert SubtotalPricingPolicy().price(cart()).amount == Decimal("100.00")


def test_percentage_discount_policy() -> None:
    discount = PercentageDiscountPolicy(Decimal("0.10")).calculate(cart())
    assert discount.amount == Decimal("10.00")


def test_vat_rate_policy() -> None:
    vat = VatRatePolicy(Decimal("0.07")).calculate(Money(Decimal("100")))
    assert vat.amount == Decimal("7.00")
