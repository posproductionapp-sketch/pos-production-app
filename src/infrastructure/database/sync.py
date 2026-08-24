"""Durable offline command ledger."""

import json
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import SyncCommandModel


class SqlAlchemySyncRepository:
    def __init__(self, session: Session, *, tenant_id: str, store_id: str) -> None:
        self.session, self.tenant_id, self.store_id = session, tenant_id, store_id

    def get(self, command_id: str) -> SyncCommandModel | None:
        return self.session.scalar(select(SyncCommandModel).where(
            SyncCommandModel.tenant_id == self.tenant_id,
            SyncCommandModel.store_id == self.store_id,
            SyncCommandModel.command_id == command_id,
        ))

    def record_received(self, *, command_id: str, operation: str, payload: dict) -> SyncCommandModel:
        existing = self.get(command_id)
        if existing:
            return existing
        row = SyncCommandModel(id=str(uuid4()), tenant_id=self.tenant_id, store_id=self.store_id,
                               command_id=command_id, operation=operation,
                               payload_json=json.dumps(payload, separators=(",", ":"), sort_keys=True), state="received")
        self.session.add(row)
        self.session.flush()
        return row

    def complete(self, command_id: str, result: dict) -> SyncCommandModel:
        row = self.get(command_id)
        if row is None:
            raise KeyError(command_id)
        row.result_json = json.dumps(result, separators=(",", ":"), sort_keys=True)
        row.state = "completed"
        self.session.flush()
        return row
