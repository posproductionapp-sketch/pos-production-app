"""Payment/refund persistence adapters."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import PaymentModel, RefundModel


class SqlAlchemyPaymentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, *, order_id: str, provider: str, provider_reference: str, amount: Decimal, currency: str, state: str) -> PaymentModel:
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
        refund = RefundModel(id=str(uuid4()), payment_id=payment_id, amount=amount, currency=currency, state=state, provider_reference=provider_reference)
        self.session.add(refund)
        self.session.flush()
        return refund
