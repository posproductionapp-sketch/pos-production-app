"""External integration adapter contracts.

Vendor SDKs belong in concrete adapters under this boundary. Core domain and
application code depend only on these stable protocols.
"""

from typing import Protocol

from src.domain.payment_stock import Payment, StockReservation
from src.domain.order import Refund


class PaymentAdapter(Protocol):
    def authorize(self, payment: Payment) -> bool: ...
    def refund(self, refund: Refund) -> bool: ...


class InventoryAdapter(Protocol):
    def reserve(self, reservation: StockReservation) -> bool: ...
    def release(self, reservation: StockReservation) -> bool: ...


class HardwareAdapter(Protocol):
    """Local hardware-agent boundary; vendor SDKs stay behind the agent."""

    def print_receipt(
        self,
        *,
        command_id: str,
        store_id: str,
        receipt_id: str,
        content: str,
    ) -> bool: ...

    def open_cash_drawer(self, *, command_id: str, store_id: str) -> bool: ...

    def health(self) -> dict[str, object]: ...
