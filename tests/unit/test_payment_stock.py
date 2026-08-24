from decimal import Decimal

import pytest

from src.domain.contracts import Money
from src.domain.payment_stock import Payment, StockReservation


def test_payment_requires_identity_and_method() -> None:
    payment = Payment("pay-1", Money(Decimal("100")), "cash")
    assert payment.payment_id == "pay-1"
    assert payment.method == "cash"


def test_payment_requires_method() -> None:
    with pytest.raises(ValueError):
        Payment("pay-1", Money(Decimal("100")), "")


def test_stock_reservation_requires_positive_quantity() -> None:
    reservation = StockReservation("coffee", Decimal("2"))
    assert reservation.quantity == Decimal("2")

    with pytest.raises(ValueError):
        StockReservation("coffee", Decimal("0"))
