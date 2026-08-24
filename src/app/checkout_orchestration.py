"""Checkout orchestration with explicit failure compensation."""

from dataclasses import dataclass

from src.app.contracts import CheckoutRequest, CheckoutResult, CheckoutServicePort
from src.app.ports import InventoryPort, PaymentGatewayPort
from src.domain.payment_stock import Payment, StockReservation


@dataclass(frozen=True)
class CheckoutExecution:
    quote: CheckoutResult
    payment_approved: bool
    stock_reserved: bool


class CheckoutOrchestrator:
    """Coordinate stock and payment without owning external implementations.

    Stock is reserved for every cart line before payment authorization. Any
    failed reservation or payment authorization compensates all reservations
    already acquired in this execution.
    """

    def __init__(
        self,
        checkout: CheckoutServicePort,
        inventory: InventoryPort,
        payments: PaymentGatewayPort,
    ) -> None:
        self._checkout = checkout
        self._inventory = inventory
        self._payments = payments

    def execute(self, request: CheckoutRequest, payment: Payment) -> CheckoutExecution:
        quote = self._checkout.quote(request)
        if not request.cart.items:
            return CheckoutExecution(quote, payment_approved=False, stock_reserved=False)
        if payment.amount.currency != quote.total.currency or payment.amount.amount != quote.total.amount:
            return CheckoutExecution(quote, payment_approved=False, stock_reserved=False)

        reservations = [
            StockReservation(item.product_id, item.quantity)
            for item in request.cart.items
        ]
        reserved: list[StockReservation] = []

        for reservation in reservations:
            if not self._inventory.reserve(reservation):
                for acquired in reversed(reserved):
                    self._inventory.release(acquired)
                return CheckoutExecution(quote, payment_approved=False, stock_reserved=False)
            reserved.append(reservation)

        if not self._payments.authorize(payment):
            for acquired in reversed(reserved):
                self._inventory.release(acquired)
            return CheckoutExecution(quote, payment_approved=False, stock_reserved=False)

        return CheckoutExecution(quote, payment_approved=True, stock_reserved=True)
