from decimal import Decimal

from src.app.checkout_orchestration import CheckoutOrchestrator
from src.app.contracts import CheckoutRequest, CheckoutService
from src.domain.contracts import Cart, LineItem, Money
from src.domain.payment_stock import Payment
from src.services.deterministic_pricing import PercentageDiscountPolicy, VatRatePolicy


class FakeInventory:
    def __init__(self, reserve_ok=True):
        self.reserve_ok = reserve_ok
        self.released = False

    def reserve(self, reservation):
        return self.reserve_ok

    def release(self, reservation):
        self.released = True
        return True


class FakePayments:
    def __init__(self, approved=True):
        self.approved = approved

    def authorize(self, payment):
        return self.approved


def checkout():
    return CheckoutService(
        pricing=None,
        discount=PercentageDiscountPolicy(Decimal("0.10")),
        vat=VatRatePolicy(Decimal("0.07")),
    )


def request():
    return CheckoutRequest(
        Cart((LineItem("coffee", Decimal("2"), Money(Decimal("50"))),))
    )


def test_payment_failure_releases_stock():
    inventory = FakeInventory()
    orchestrator = CheckoutOrchestrator(checkout(), inventory, FakePayments(False))
    result = orchestrator.execute(request(), Payment("pay-1", Money(Decimal("96.30")), "cash"))

    assert not result.payment_approved
    assert not result.stock_reserved
    assert inventory.released


def test_success_keeps_stock_reserved():
    inventory = FakeInventory()
    orchestrator = CheckoutOrchestrator(checkout(), inventory, FakePayments(True))
    result = orchestrator.execute(request(), Payment("pay-1", Money(Decimal("96.30")), "cash"))

    assert result.payment_approved
    assert result.stock_reserved
    assert not inventory.released
