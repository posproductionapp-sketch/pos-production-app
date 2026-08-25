from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.infrastructure.database.models import Base, StoreModel
from src.infrastructure.database.sync import SqlAlchemySyncRepository


def test_sync_command_is_idempotent_and_terminal_completion_is_stable():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(StoreModel(id="store-1", tenant_id="tenant-1", name="Test"))
        session.commit()
        repo = SqlAlchemySyncRepository(session, tenant_id="tenant-1", store_id="store-1")
        first = repo.record_received(command_id="cmd-1", operation="sale", payload={"order_id": "o1"})
        duplicate = repo.record_received(command_id="cmd-1", operation="sale", payload={"order_id": "different"})
        assert duplicate.id == first.id
        repo.complete("cmd-1", {"order_id": "o1"})
        completed = repo.complete("cmd-1", {"order_id": "changed"})
        assert completed.result_json == '{"order_id":"o1"}'
