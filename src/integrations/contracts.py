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
