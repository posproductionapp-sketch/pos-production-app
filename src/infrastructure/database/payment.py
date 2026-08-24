"""Payment/refund persistence adapters with financial invariants."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import OrderModel, PaymentModel, RefundModel


class RefundExceedsPayment(ValueError):
    pass


class PaymentConflict(ValueError):
    pass


class SqlAlchemyPaymentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, *, order_id: str, provider: str, provider_reference: str, amount: Decimal, currency: str, state: str) -> PaymentModel:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        order = self.session.scalar(select(OrderModel).where(OrderModel.id == order_id).with_for_update())
        if order is None:
            raise KeyError(order_id)
        if order.total_amount != amount or order.currency != currency:
            raise PaymentConflict("Payment amount/currency must match order total")
        existing = self.session.scalar(select(PaymentModel).where(PaymentModel.provider == provider, PaymentModel.provider_reference == provider_reference))
        if existing:
            if existing.order_id != order_id or existing.amount != amount or existing.currency != currency:
                raise PaymentConflict("Provider reference is already bound to a different payment")
            return existing
        payment = PaymentModel(id=str(uuid4()), order_id=order_id, provider=provider, provider_reference=provider_reference, amount=amount, currency=currency, state=state, created_at=datetime.now(timezone.utc))
        self.session.add(payment)
        self.session.flush()
        return payment


class SqlAlchemyRefundRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, *, payment_id: str, amount: Decimal, currency: str, state: str, provider_reference: str) -> RefundModel:
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        payment = self.session.scalar(select(PaymentModel).where(PaymentModel.id == payment_id).with_for_update())
        if payment is None:
            raise KeyError(payment_id)
        if payment.currency != currency:
            raise ValueError("Refund currency must match payment currency")
        existing = self.session.scalar(select(RefundModel).where(RefundModel.payment_id == payment_id, RefundModel.provider_reference == provider_reference))
        if existing:
            if existing.amount != amount or existing.currency != currency:
                raise RefundExceedsPayment("Refund provider reference is already bound to another refund")
            return existing
        refunded = self.session.scalar(select(func.coalesce(func.sum(RefundModel.amount), 0)).where(RefundModel.payment_id == payment_id)) or Decimal("0")
        if refunded + amount > payment.amount:
            raise RefundExceedsPayment("Cumulative refunds cannot exceed payment amount")
        refund = RefundModel(id=str(uuid4()), payment_id=payment_id, amount=amount, currency=currency, state=state, provider_reference=provider_reference, created_at=datetime.now(timezone.utc))
        self.session.add(refund)
        self.session.flush()
        return refund
