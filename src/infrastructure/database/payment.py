"""Payment/refund persistence adapters with financial invariants."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import PaymentModel, RefundModel


class RefundExceedsPayment(ValueError):
    pass


class SqlAlchemyPaymentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, *, order_id: str, provider: str, provider_reference: str, amount: Decimal, currency: str, state: str) -> PaymentModel:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        existing = self.session.scalar(select(PaymentModel).where(PaymentModel.provider == provider, PaymentModel.provider_reference == provider_reference))
        if existing:
            return existing
        payment = PaymentModel(id=str(uuid4()), order_id=order_id, provider=provider, provider_reference=provider_reference, amount=amount, currency=currency, state=state)
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
        refunded = self.session.scalar(select(func.coalesce(func.sum(RefundModel.amount), 0)).where(RefundModel.payment_id == payment_id)) or Decimal("0")
        if refunded + amount > payment.amount:
            raise RefundExceedsPayment("Cumulative refunds cannot exceed payment amount")
        refund = RefundModel(id=str(uuid4()), payment_id=payment_id, amount=amount, currency=currency, state=state, provider_reference=provider_reference)
        self.session.add(refund)
        self.session.flush()
        return refund
