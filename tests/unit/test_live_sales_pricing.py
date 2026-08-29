"""Financial regression cases for deterministic checkout pricing."""

from decimal import Decimal

import pytest

from src.app.contracts import CheckoutRequest
from src.domain.contracts import Cart, LineItem, Money
from src.services.checkout import CheckoutService
from src.services.deterministic_pricing import PercentageDiscountPolicy, SubtotalPricingPolicy, VatRatePolicy


def quote(price: str, quantity: str = "1", *, vat: str = "0", discount: str = "0"):
    cart = Cart((LineItem("v", Decimal(quantity), Money(Decimal(price), "THB")),))
    return CheckoutService(SubtotalPricingPolicy(), PercentageDiscountPolicy(Decimal(discount)), VatRatePolicy(Decimal(vat))).quote(CheckoutRequest(cart))


@pytest.mark.parametrize(
    ("vat", "discount", "subtotal", "discount_amount", "tax", "total"),
    [
        ("0", "0", "100.00", "0.00", "0.00", "100.00"),
        ("0.07", "0", "100.00", "0.00", "7.00", "107.00"),
        ("0", "0.10", "100.00", "10.00", "0.00", "90.00"),
        ("0.07", "0.10", "100.00", "10.00", "6.30", "96.30"),
        ("0.07", "0.10", "99.99", "10.00", "6.30", "96.29"),
    ],
)
def test_financial_integrity_cases(vat, discount, subtotal, discount_amount, tax, total):
    result = quote("99.99" if subtotal == "99.99" else "100", vat=vat, discount=discount)
    assert result.subtotal.amount == Decimal(subtotal)
    assert result.discount.amount == Decimal(discount_amount)
    assert result.vat.amount == Decimal(tax)
    assert result.total.amount == Decimal(total)
