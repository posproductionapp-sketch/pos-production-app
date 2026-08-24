"""Application refund port."""

from typing import Protocol

from src.domain.order import Order, OrderState, Refund


class RefundGatewayPort(Protocol):
    def refund(self, refund: Refund) -> bool:
        """Execute a refund through an injected payment adapter."""


class RefundService:
    def __init__(self, gateway: RefundGatewayPort) -> None:
        self._gateway = gateway

    def execute(self, order: Order, refund: Refund) -> Order:
        if refund.order_id != order.order_id:
            raise ValueError("Refund does not belong to order")
        if refund.amount.currency != order.total.currency:
            raise ValueError("Refund currency must match order currency")
        if refund.amount.amount > order.total.amount:
            raise ValueError("Refund cannot exceed order total")
        if order.state not in {OrderState.PAID, OrderState.COMPLETED}:
            raise ValueError("Only paid or completed orders can be refunded")
        if not self._gateway.refund(refund):
            raise RuntimeError("Refund gateway rejected refund")
        return order.transition(OrderState.REFUND_PENDING).transition(OrderState.REFUNDED)
