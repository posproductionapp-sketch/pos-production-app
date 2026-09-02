"""Unit gates for the authoritative sync dispatcher."""

import pytest

from src.app.sync_dispatcher import (
    AuthoritativeSyncDispatcher,
    DispatchContext,
    SyncOperationNotSupported,
)


CONTEXT = DispatchContext(
    command_id="cmd-1",
    tenant_id="tenant-1",
    store_id="store-1",
    actor_id="user-1",
)


def test_dispatch_requires_explicit_operation_registration() -> None:
    dispatcher = AuthoritativeSyncDispatcher()

    with pytest.raises(SyncOperationNotSupported):
        dispatcher.dispatch("sale", {"amount": "10.00"}, CONTEXT)


def test_dispatch_passes_authenticated_scope_and_command_identity_to_handler() -> None:
    dispatcher = AuthoritativeSyncDispatcher()
    observed = {}

    def handler(payload, context):
        observed["payload"] = payload
        observed["context"] = context
        return {"order_id": "order-1", "state": "paid"}

    dispatcher.register("sale", handler)
    result = dispatcher.dispatch("sale", {"amount": "10.00"}, CONTEXT)

    assert result == {"order_id": "order-1", "state": "paid"}
    assert observed["payload"] == {"amount": "10.00"}
    assert observed["context"] == CONTEXT


def test_register_rejects_duplicate_operation() -> None:
    dispatcher = AuthoritativeSyncDispatcher()
    dispatcher.register("sale", lambda payload, context: payload)

    with pytest.raises(ValueError):
        dispatcher.register("sale", lambda payload, context: payload)


def test_supported_operations_are_deterministic() -> None:
    dispatcher = AuthoritativeSyncDispatcher()
    dispatcher.register("refund", lambda payload, context: payload)
    dispatcher.register("sale", lambda payload, context: payload)

    assert dispatcher.supported_operations() == ("refund", "sale")
