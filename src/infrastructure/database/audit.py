"""Append-only audit persistence adapter."""

import json
from uuid import uuid4

from sqlalchemy.orm import Session

from src.infrastructure.database.models import AuditLogModel


class SqlAlchemyAuditRepository:
    def __init__(self, session: Session, *, tenant_id: str, store_id: str) -> None:
        self.session, self.tenant_id, self.store_id = session, tenant_id, store_id

    def append(self, *, actor_id: str, action: str, resource_type: str, resource_id: str, correlation_id: str, metadata: dict) -> AuditLogModel:
        record = AuditLogModel(
            id=str(uuid4()), tenant_id=self.tenant_id, store_id=self.store_id,
            actor_id=actor_id, action=action, resource_type=resource_type,
            resource_id=resource_id, correlation_id=correlation_id,
            metadata_json=json.dumps(metadata, separators=(",", ":"), sort_keys=True),
        )
        self.session.add(record)
        self.session.flush()
        return record
