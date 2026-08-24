from decimal import Decimal

import pytest

from src.app.contracts import CheckoutRequest
from src.domain.contracts import Cart, LineItem, Money
from src.services.checkout import CheckoutService
from src.services.deterministic_pricing import (
    PercentageDiscountPolicy,
    SubtotalPricingPolicy,
    VatRatePolicy,
)


def cart() -> Cart:
    return Cart((LineItem("coffee", Decimal("2"), Money(Decimal("50"))),))


def service(discount_rate: str = "0.10") -> CheckoutService:
    return CheckoutService(
        pricing=SubtotalPricingPolicy(),
        discount=PercentageDiscountPolicy(Decimal(discount_rate)),
        vat=VatRatePolicy(Decimal("0.07")),
    )


def test_quote_applies_discount_before_vat():
    result = service().quote(CheckoutRequest(cart()))

    assert result.subtotal == Money(Decimal("100"))
    assert result.discount == Money(Decimal("10"))
    assert result.vat == Money(Decimal("6.30"))
    assert result.total == Money(Decimal("96.30"))


def test_quote_rejects_discount_that_exceeds_subtotal():
    class ExcessiveDiscount:
        def calculate(self, _cart):
            return Money(Decimal("101"))

    checkout = CheckoutService(
        pricing=SubtotalPricingPolicy(),
        discount=ExcessiveDiscount(),
        vat=VatRatePolicy(Decimal("0.07")),
    )

    with pytest.raises(ValueError, match="Discount cannot exceed subtotal"):
        checkout.quote(CheckoutRequest(cart()))


def test_quote_rejects_discount_currency_mismatch():
    class ForeignDiscount:
        def calculate(self, _cart):
            return Money(Decimal("10"), "USD")

    checkout = CheckoutService(
        pricing=SubtotalPricingPolicy(),
        discount=ForeignDiscount(),
        vat=VatRatePolicy(Decimal("0.07")),
    )

    with pytest.raises(ValueError, match="Discount currency"):
        checkout.quote(CheckoutRequest(cart()))


def test_quote_rejects_vat_currency_mismatch():
    class ForeignVat:
        def calculate(self, _subtotal):
            return Money(Decimal("7"), "USD")

    checkout = CheckoutService(
        pricing=SubtotalPricingPolicy(),
        discount=PercentageDiscountPolicy(Decimal("0.10")),
        vat=ForeignVat(),
    )

    with pytest.raises(ValueError, match="VAT currency"):
        checkout.quote(CheckoutRequest(cart()))


def test_quote_accepts_zero_discount_and_zero_vat():
    checkout = CheckoutService(
        pricing=SubtotalPricingPolicy(),
        discount=PercentageDiscountPolicy(Decimal("0")),
        vat=VatRatePolicy(Decimal("0")),
    )

    result = checkout.quote(CheckoutRequest(cart()))

    assert result.discount == Money(Decimal("0"))
    assert result.vat == Money(Decimal("0"))
    assert result.total == result.subtotal == Money(Decimal("100"))
