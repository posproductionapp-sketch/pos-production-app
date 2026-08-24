from decimal import Decimal

from src.domain.contracts import Money
from src.domain.order import Refund
from src.domain.payment_stock import Payment, StockReservation
from src.integrations.contracts import InventoryAdapter, PaymentAdapter


class FakePayment:
    def authorize(self, payment):
        return True

    def refund(self, refund):
        return True


class FakeInventory:
    def reserve(self, reservation):
        return True

    def release(self, reservation):
        return True


def test_external_adapters_match_stable_contracts():
    payment: PaymentAdapter = FakePayment()
    inventory: InventoryAdapter = FakeInventory()

    p = Payment("pay-1", Money(Decimal("100")), "cash")
    r = Refund("refund-1", "order-1", Money(Decimal("50")))
    s = StockReservation("coffee", Decimal("2"))

    assert payment.authorize(p)
    assert payment.refund(r)
    assert inventory.reserve(s)
    assert inventory.release(s)
