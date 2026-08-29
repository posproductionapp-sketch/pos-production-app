"""Transactional shift and cash repositories."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import StoreModel
from src.infrastructure.database.shift_models import CashMovementModel, ShiftModel


class ShiftRepository:
    def __init__(self, session: Session, *, tenant_id: str, store_id: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.store_id = store_id

    def open(self, *, actor_id: str, opening_cash: Decimal) -> ShiftModel:
        if opening_cash < 0:
            raise ValueError("Opening cash cannot be negative")
        # Lock the store row so concurrent open attempts serialize even when
        # there is currently no open shift row to lock.
        store = self.session.scalar(select(StoreModel).where(StoreModel.id == self.store_id).with_for_update())
        if store is None or store.tenant_id != self.tenant_id:
            raise ValueError("Store not found")
        existing = self.session.scalar(select(ShiftModel).where(ShiftModel.store_id == self.store_id, ShiftModel.state == "open").with_for_update())
        if existing:
            raise ValueError("An open shift already exists for this store")
        row = ShiftModel(id=str(uuid4()), tenant_id=self.tenant_id, store_id=self.store_id, opened_by=actor_id, opened_at=datetime.now(timezone.utc), opening_cash=opening_cash, state="open")
        self.session.add(row)
        self.session.flush()
        return row

    def current(self) -> ShiftModel | None:
        return self.session.scalar(select(ShiftModel).where(ShiftModel.store_id == self.store_id, ShiftModel.tenant_id == self.tenant_id, ShiftModel.state == "open").with_for_update())

    def add_cash_movement(self, *, shift_id: str, movement_type: str, amount: Decimal, reason: str, actor_id: str, correlation_id: str) -> CashMovementModel:
        if amount <= 0:
            raise ValueError("Cash movement amount must be positive")
        shift = self.session.scalar(select(ShiftModel).where(ShiftModel.id == shift_id, ShiftModel.store_id == self.store_id, ShiftModel.tenant_id == self.tenant_id).with_for_update())
        if shift is None or shift.state != "open":
            raise ValueError("Open shift is required")
        row = CashMovementModel(id=str(uuid4()), shift_id=shift_id, type=movement_type, amount=amount, reason=reason, actor_id=actor_id, correlation_id=correlation_id, created_at=datetime.now(timezone.utc))
        self.session.add(row)
        self.session.flush()
        return row

    def close(self, *, actor_id: str, closing_cash: Decimal) -> ShiftModel:
        if closing_cash < 0:
            raise ValueError("Closing cash cannot be negative")
        shift = self.current()
        if shift is None:
            raise ValueError("No open shift")
        shift.closing_cash = closing_cash
        shift.closed_by = actor_id
        shift.closed_at = datetime.now(timezone.utc)
        shift.state = "closed"
        self.session.flush()
        return shift
