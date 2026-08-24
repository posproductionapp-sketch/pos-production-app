"""Checkout orchestration with explicit failure compensation."""

from dataclasses import dataclass

from src.app.contracts import CheckoutRequest, CheckoutResult, CheckoutService
from src.app.ports import InventoryPort, PaymentGatewayPort
from src.domain.payment_stock import Payment, StockReservation


@dataclass(frozen=True)
class CheckoutExecution:
    quote: CheckoutResult
    payment_approved: bool
    stock_reserved: bool


class CheckoutOrchestrator:
    """Coordinate stock and payment without owning external implementations.

    Ordering is deliberate: reserve stock first, authorize payment second.
    If payment fails, the reservation is released. If payment succeeds, the
    reservation remains held for the later order/persistence phase.
    """

    def __init__(
        self,
        checkout: CheckoutService,
        inventory: InventoryPort,
        payments: PaymentGatewayPort,
    ) -> None:
        self._checkout = checkout
        self._inventory = inventory
        self._payments = payments

    def execute(self, request: CheckoutRequest, payment: Payment) -> CheckoutExecution:
        quote = self._checkout.quote(request)
        reservation = StockReservation(
            product_id=request.cart.items[0].product_id,
            quantity=request.cart.items[0].quantity,
        )

        if not self._inventory.reserve(reservation):
            return CheckoutExecution(quote, payment_approved=False, stock_reserved=False)

        if not self._payments.authorize(payment):
            self._inventory.release(reservation)
            return CheckoutExecution(quote, payment_approved=False, stock_reserved=False)

        return CheckoutExecution(quote, payment_approved=True, stock_reserved=True)
