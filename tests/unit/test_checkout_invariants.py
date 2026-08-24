from decimal import Decimal

from src.app.checkout_orchestration import CheckoutOrchestrator
from src.app.contracts import CheckoutRequest
from src.domain.contracts import Cart, LineItem, Money
from src.domain.payment_stock import Payment
from src.services.checkout import CheckoutService
from src.services.deterministic_pricing import (
    PercentageDiscountPolicy,
    SubtotalPricingPolicy,
    VatRatePolicy,
)


class Inventory:
    def __init__(self, fail_product=None):
        self.fail_product = fail_product
        self.reserved = []
        self.released = []

    def reserve(self, reservation):
        if reservation.product_id == self.fail_product:
            return False
        self.reserved.append(reservation)
        return True

    def release(self, reservation):
        self.released.append(reservation)
        return True


class Payments:
    def __init__(self, approved=True):
        self.approved = approved

    def authorize(self, payment):
        return self.approved


def service():
    return CheckoutService(
        SubtotalPricingPolicy(),
        PercentageDiscountPolicy(Decimal("0.10")),
        VatRatePolicy(Decimal("0.07")),
    )


def test_multiple_reservations_are_compensated_atomically():
    cart = Cart((
        LineItem("coffee", Decimal("1"), Money(Decimal("50"))),
        LineItem("cake", Decimal("1"), Money(Decimal("50"))),
    ))
    inventory = Inventory(fail_product="cake")
    result = CheckoutOrchestrator(service(), inventory, Payments()).execute(
        CheckoutRequest(cart), Payment("pay-1", Money(Decimal("96.30")), "cash")
    )

    assert not result.stock_reserved
    assert inventory.reserved[0].product_id == "coffee"
    assert inventory.released[0].product_id == "coffee"


def test_payment_amount_must_match_quote():
    cart = Cart((LineItem("coffee", Decimal("2"), Money(Decimal("50"))),))
    inventory = Inventory()
    result = CheckoutOrchestrator(service(), inventory, Payments()).execute(
        CheckoutRequest(cart), Payment("pay-1", Money(Decimal("95")), "cash")
    )

    assert not result.payment_approved
    assert not inventory.reserved
