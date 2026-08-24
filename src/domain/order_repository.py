"""Persistence boundary for orders; implementations belong outside domain."""

from typing import Protocol

from src.domain.order import Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        """Persist an order."""

    def get(self, order_id: str) -> Order | None:
        """Return an order by id, or None when absent."""
