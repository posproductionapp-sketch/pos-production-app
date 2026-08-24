"""Durable, transaction-aware idempotency adapter."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infrastructure.database.models import IdempotencyKeyModel


class IdempotencyConflict(Exception):
    pass


class SqlAlchemyIdempotencyRepository:
    def __init__(self, session: Session, *, tenant_id: str, store_id: str) -> None:
        self.session, self.tenant_id, self.store_id = session, tenant_id, store_id

    def get(self, operation: str, key: str) -> IdempotencyKeyModel | None:
        return self.session.scalar(select(IdempotencyKeyModel).where(
            IdempotencyKeyModel.tenant_id == self.tenant_id,
            IdempotencyKeyModel.store_id == self.store_id,
            IdempotencyKeyModel.operation == operation,
            IdempotencyKeyModel.key == key,
        ))

    def reserve(self, operation: str, key: str, result_reference: str) -> IdempotencyKeyModel:
        existing = self.get(operation, key)
        if existing is not None:
            if existing.result_reference != result_reference:
                raise IdempotencyConflict("Idempotency key is already bound to another result")
            return existing
        record = IdempotencyKeyModel(
            id=f"{self.tenant_id}:{self.store_id}:{operation}:{key}",
            tenant_id=self.tenant_id, store_id=self.store_id,
            operation=operation, key=key, result_reference=result_reference,
        )
        self.session.add(record)
        try:
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            existing = self.get(operation, key)
            if existing is None:
                raise
            return existing
        return record
