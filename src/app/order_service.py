"""Application service for order lifecycle persistence."""

from src.domain.order import Order, OrderState
from src.domain.order_repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def complete(self, order_id: str) -> Order:
        order = self._repository.get(order_id)
        if order is None:
            raise LookupError(f"Order not found: {order_id}")
        if order.state != OrderState.PAID:
            raise ValueError("Only paid orders can be completed")
        completed = order.transition(OrderState.COMPLETED)
        self._repository.save(completed)
        return completed
