"""Durable, tenant/store/principal-scoped offline command ledger."""

import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infrastructure.database.models import SyncCommandModel


class SyncCommandConflict(Exception):
    """Raised when a command id is reused by another logical command or actor."""


class SqlAlchemySyncRepository:
    def __init__(self, session: Session, *, tenant_id: str, store_id: str, actor_id: str) -> None:
        if not tenant_id or not store_id or not actor_id:
            raise ValueError("tenant_id, store_id and actor_id are required")
        self.session, self.tenant_id, self.store_id, self.actor_id = session, tenant_id, store_id, actor_id

    def get(self, command_id: str) -> SyncCommandModel | None:
        return self.session.scalar(select(SyncCommandModel).where(
            SyncCommandModel.tenant_id == self.tenant_id,
            SyncCommandModel.store_id == self.store_id,
            SyncCommandModel.command_id == command_id,
        ))

    def record_received(self, *, command_id: str, operation: str, payload: dict) -> SyncCommandModel:
        existing = self.get(command_id)
        if existing:
            if existing.actor_id != self.actor_id or existing.operation != operation or json.loads(existing.payload_json) != payload:
                raise SyncCommandConflict("Command identity is already bound to another principal or payload")
            return existing
        row = SyncCommandModel(id=str(uuid4()), tenant_id=self.tenant_id, store_id=self.store_id,
                               actor_id=self.actor_id, command_id=command_id, operation=operation,
                               payload_json=json.dumps(payload, separators=(",", ":"), sort_keys=True), state="received")
        self.session.add(row)
        try:
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            existing = self.get(command_id)
            if existing:
                if existing.actor_id != self.actor_id or existing.operation != operation or json.loads(existing.payload_json) != payload:
                    raise SyncCommandConflict("Command identity is already bound to another principal or payload")
                return existing
            raise
        return row

    def claim(self, command_id: str, *, lease_seconds: int = 60) -> SyncCommandModel:
        row = self.get(command_id)
        if row is None:
            raise KeyError(command_id)
        if row.actor_id != self.actor_id:
            raise SyncCommandConflict("Command belongs to another principal")
        if row.state == "completed" or row.state == "failed":
            return row
        row.state = "sending"
        row.attempt_count += 1
        row.lease_until = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
        self.session.flush()
        return row

    def recover_stale_sending(self, *, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        rows = self.session.scalars(select(SyncCommandModel).where(
            SyncCommandModel.tenant_id == self.tenant_id,
            SyncCommandModel.store_id == self.store_id,
            SyncCommandModel.actor_id == self.actor_id,
            SyncCommandModel.state == "sending",
            SyncCommandModel.lease_until.is_not(None),
            SyncCommandModel.lease_until <= now,
        )).all()
        for row in rows:
            row.state = "received"
            row.lease_until = None
        self.session.flush()
        return len(rows)

    def complete(self, command_id: str, result: dict) -> SyncCommandModel:
        row = self.get(command_id)
        if row is None:
            raise KeyError(command_id)
        if row.actor_id != self.actor_id:
            raise SyncCommandConflict("Command belongs to another principal")
        if row.state == "completed":
            return row
        row.result_json = json.dumps(result, separators=(",", ":"), sort_keys=True)
        row.state = "completed"
        row.lease_until = None
        self.session.flush()
        return row

    def fail(self, command_id: str, error_code: str) -> SyncCommandModel:
        row = self.get(command_id)
        if row is None:
            raise KeyError(command_id)
        if row.actor_id != self.actor_id:
            raise SyncCommandConflict("Command belongs to another principal")
        if row.state == "completed":
            return row
        row.result_json = json.dumps({"error": error_code}, separators=(",", ":"), sort_keys=True)
        row.state = "failed"
        row.lease_until = None
        self.session.flush()
        return row
