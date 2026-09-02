"""Integration coverage for the durable offline command ledger."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.infrastructure.database.models import Base
from src.infrastructure.database.sync import SqlAlchemySyncRepository


def session_factory() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine, expire_on_commit=False)


def test_duplicate_command_is_durable_and_does_not_replace_payload() -> None:
    session = session_factory()
    repository = SqlAlchemySyncRepository(
        session, tenant_id="tenant-a", store_id="store-a", actor_id="actor-a"
    )

    first = repository.record_received(
        command_id="cmd-1",
        operation="sale",
        payload={"amount": "10.00", "currency": "THB"},
    )
    session.commit()

    duplicate = repository.record_received(
        command_id="cmd-1",
        operation="sale",
        payload={"amount": "999.00", "currency": "THB"},
    )

    assert duplicate.id == first.id
    assert duplicate.payload_json == '{"amount":"10.00","currency":"THB"}'
    assert duplicate.state == "received"


def test_completion_is_idempotent_and_persists_authoritative_result() -> None:
    session = session_factory()
    repository = SqlAlchemySyncRepository(
        session, tenant_id="tenant-a", store_id="store-a", actor_id="actor-a"
    )
    repository.record_received(command_id="cmd-2", operation="sale", payload={"order": "o-2"})
    session.commit()

    completed = repository.complete("cmd-2", {"order_id": "o-2", "state": "paid"})
    session.commit()
    replay = repository.complete("cmd-2", {"order_id": "o-other", "state": "paid"})

    assert replay.id == completed.id
    assert replay.result_json == '{"order_id":"o-2","state":"paid"}'
    assert replay.state == "completed"


def test_failed_command_retains_error_and_is_not_overwritten_after_completion() -> None:
    session = session_factory()
    repository = SqlAlchemySyncRepository(
        session, tenant_id="tenant-a", store_id="store-a", actor_id="actor-a"
    )
    repository.record_received(command_id="cmd-3", operation="sale", payload={"order": "o-3"})
    session.commit()

    failed = repository.fail("cmd-3", "insufficient_inventory")
    session.commit()
    completed = repository.complete("cmd-3", {"order_id": "o-3"})

    assert completed.id == failed.id
    assert completed.state == "failed"
    assert completed.result_json == '{"error":"insufficient_inventory"}'


def test_command_scope_isolated_by_tenant_and_store() -> None:
    session = session_factory()
    tenant_a = SqlAlchemySyncRepository(
        session, tenant_id="tenant-a", store_id="store-a", actor_id="actor-a"
    )
    tenant_b = SqlAlchemySyncRepository(
        session, tenant_id="tenant-b", store_id="store-a", actor_id="actor-a"
    )
    store_b = SqlAlchemySyncRepository(
        session, tenant_id="tenant-a", store_id="store-b", actor_id="actor-a"
    )

    tenant_a.record_received(command_id="shared-id", operation="sale", payload={"owner": "a"})
    session.commit()

    assert tenant_b.get("shared-id") is None
    assert store_b.get("shared-id") is None
