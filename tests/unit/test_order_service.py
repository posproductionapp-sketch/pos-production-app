from decimal import Decimal

import pytest

from src.app.order_service import OrderService
from src.domain.contracts import Money
from src.domain.order import Order, OrderState


class MemoryOrderRepository:
    def __init__(self, order=None):
        self.order = order

    def get(self, order_id):
        return self.order if self.order and self.order.order_id == order_id else None

    def save(self, order):
        self.order = order


def test_complete_persists_paid_order():
    repo = MemoryOrderRepository(Order("o-1", Money(Decimal("100")), OrderState.PAID))
    result = OrderService(repo).complete("o-1")
    assert result.state == OrderState.COMPLETED
    assert repo.order.state == OrderState.COMPLETED


def test_complete_rejects_non_paid_order():
    repo = MemoryOrderRepository(Order("o-1", Money(Decimal("100")), OrderState.PENDING))
    with pytest.raises(ValueError):
        OrderService(repo).complete("o-1")


def test_complete_requires_existing_order():
    with pytest.raises(LookupError):
        OrderService(MemoryOrderRepository()).complete("missing")
