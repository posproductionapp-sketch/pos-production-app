"""Application ports for external payment and inventory capabilities."""

from typing import Protocol

from src.domain.payment_stock import Payment, StockReservation


class PaymentGatewayPort(Protocol):
    def authorize(self, payment: Payment) -> bool:
        """Authorize payment without exposing a vendor implementation."""


class InventoryPort(Protocol):
    def reserve(self, reservation: StockReservation) -> bool:
        """Reserve inventory without exposing persistence details."""

    def release(self, reservation: StockReservation) -> bool:
        """Release inventory without exposing persistence details."""
