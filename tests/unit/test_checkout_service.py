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
