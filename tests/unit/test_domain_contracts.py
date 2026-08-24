from decimal import Decimal

import pytest

from src.domain.contracts import Cart, LineItem, Money


def test_cart_subtotal_is_deterministic() -> None:
    cart = Cart(
        items=(
            LineItem("coffee", Decimal("2"), Money(Decimal("50"))),
            LineItem("cake", Decimal("1"), Money(Decimal("80"))),
        )
    )
    assert cart.subtotal().amount == Decimal("180")
    assert cart.subtotal().currency == "THB"


def test_negative_money_is_rejected() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("-1"))


def test_non_positive_quantity_is_rejected() -> None:
    with pytest.raises(ValueError):
        LineItem("coffee", Decimal("0"), Money(Decimal("50")))
