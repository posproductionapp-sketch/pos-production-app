from decimal import Decimal

from src.app.contracts import CheckoutRequest, CheckoutService
from src.domain.contracts import Cart, LineItem, Money
from src.services.deterministic_pricing import PercentageDiscountPolicy, VatRatePolicy


def test_checkout_applies_discount_then_vat() -> None:
    cart = Cart((LineItem("coffee", Decimal("2"), Money(Decimal("50"))),))
    checkout = CheckoutService(
        pricing=None,
        discount=PercentageDiscountPolicy(Decimal("0.10")),
        vat=VatRatePolicy(Decimal("0.07")),
    )

    result = checkout.quote(CheckoutRequest(cart))

    assert result.subtotal.amount == Decimal("100.00")
    assert result.discount.amount == Decimal("10.00")
    assert result.vat.amount == Decimal("6.30")
    assert result.total.amount == Decimal("96.30")
