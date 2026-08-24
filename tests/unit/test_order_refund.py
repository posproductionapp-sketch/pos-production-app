from decimal import Decimal

import pytest

from src.app.refund import RefundService
from src.domain.contracts import Money
from src.domain.order import Order, OrderState, Refund


class FakeRefundGateway:
    def __init__(self, approved=True):
        self.approved = approved

    def refund(self, refund):
        return self.approved


def paid_order():
    return Order("order-1", Money(Decimal("100")), OrderState.PAID)


def test_order_rejects_invalid_transition():
    with pytest.raises(ValueError):
        paid_order().transition(OrderState.PENDING)


def test_refund_completes_order_lifecycle():
    service = RefundService(FakeRefundGateway())
    refund = Refund("refund-1", "order-1", Money(Decimal("50")))

    result = service.execute(paid_order(), refund)

    assert result.state == OrderState.REFUNDED


def test_refund_cannot_exceed_total():
    service = RefundService(FakeRefundGateway())
    refund = Refund("refund-1", "order-1", Money(Decimal("101")))

    with pytest.raises(ValueError):
        service.execute(paid_order(), refund)


def test_rejected_refund_does_not_transition():
    service = RefundService(FakeRefundGateway(False))
    refund = Refund("refund-1", "order-1", Money(Decimal("50")))

    with pytest.raises(RuntimeError):
        service.execute(paid_order(), refund)
