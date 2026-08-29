"""Concurrency-safe inventory persistence adapter."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import InventoryBalanceModel, InventoryMovementModel


class InventoryInsufficientStock(Exception):
    pass


class SqlAlchemyInventoryRepository:
    def __init__(self, session: Session, *, store_id: str) -> None:
        if not store_id:
            raise ValueError("store_id is required")
        self.session = session
        self.store_id = store_id

    def quantity(self, *, variant_id: str, lock: bool = False) -> Decimal:
        statement = select(InventoryBalanceModel).where(
            InventoryBalanceModel.store_id == self.store_id,
            InventoryBalanceModel.variant_id == variant_id,
        )
        if lock:
            statement = statement.with_for_update()
        row = self.session.scalar(statement)
        return row.quantity if row is not None else Decimal("0")

    def adjust(self, *, variant_id: str, delta: Decimal, reason: str, correlation_id: str) -> Decimal:
        if delta == 0:
            raise ValueError("Inventory delta cannot be zero")
        now = datetime.now(timezone.utc)
        row = self.session.scalar(
            select(InventoryBalanceModel)
            .where(InventoryBalanceModel.store_id == self.store_id, InventoryBalanceModel.variant_id == variant_id)
            .with_for_update()
        )
        if row is None:
            if delta < 0:
                raise InventoryInsufficientStock("No inventory balance exists")
            row = InventoryBalanceModel(id=str(uuid4()), store_id=self.store_id, variant_id=variant_id, quantity=Decimal("0"), updated_at=now)
            self.session.add(row)
            self.session.flush()
        new_quantity = row.quantity + delta
        if new_quantity < 0:
            raise InventoryInsufficientStock("Inventory cannot become negative")
        row.quantity = new_quantity
        row.updated_at = now
        self.session.add(InventoryMovementModel(id=str(uuid4()), store_id=self.store_id, variant_id=variant_id, quantity_delta=delta, reason=reason, correlation_id=correlation_id, created_at=now))
        self.session.flush()
        return new_quantity
