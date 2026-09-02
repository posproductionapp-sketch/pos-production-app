import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.infrastructure.database.models import Base, StoreModel
from src.infrastructure.database.sync import SqlAlchemySyncRepository, SyncCommandConflict


def test_sync_command_is_idempotent_and_terminal_completion_is_stable():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(StoreModel(id="store-1", tenant_id="tenant-1", name="Test"))
        session.commit()
        repo = SqlAlchemySyncRepository(session, tenant_id="tenant-1", store_id="store-1", actor_id="user-1")
        first = repo.record_received(command_id="cmd-1", operation="sale", payload={"order_id": "o1"})
        duplicate = repo.record_received(command_id="cmd-1", operation="sale", payload={"order_id": "o1"})
        assert duplicate.id == first.id
        with pytest.raises(SyncCommandConflict):
            repo.record_received(command_id="cmd-1", operation="sale", payload={"order_id": "different"})
        repo.complete("cmd-1", {"order_id": "o1"})
        completed = repo.complete("cmd-1", {"order_id": "changed"})
        assert completed.result_json == '{"order_id":"o1"}'


def test_sync_command_rejects_other_actor_and_recovers_stale_send():
    from datetime import datetime, timedelta, timezone

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(StoreModel(id="store-1", tenant_id="tenant-1", name="Test"))
        session.commit()
        repo = SqlAlchemySyncRepository(session, tenant_id="tenant-1", store_id="store-1", actor_id="user-1")
        repo.record_received(command_id="cmd-2", operation="sale", payload={"order_id": "o2"})
        repo.claim("cmd-2", lease_seconds=1)
        row = repo.get("cmd-2")
        row.lease_until = datetime.now(timezone.utc) - timedelta(seconds=1)
        session.flush()
        assert repo.recover_stale_sending() == 1
        assert repo.get("cmd-2").state == "received"

        other = SqlAlchemySyncRepository(session, tenant_id="tenant-1", store_id="store-1", actor_id="user-2")
        with pytest.raises(SyncCommandConflict):
            other.claim("cmd-2")
