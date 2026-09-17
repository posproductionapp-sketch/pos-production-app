"""Authoritative sync dispatch contract for server-side mutation replay."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


class SyncDispatchError(Exception):
    """Base error for sync dispatch failures."""


class SyncOperationNotSupported(SyncDispatchError):
    """Raised when an operation has no explicitly registered handler."""


@dataclass(frozen=True)
class DispatchContext:
    command_id: str
    tenant_id: str
    store_id: str
    actor_id: str


class AuthoritativeSyncDispatcher:
    """Dispatch only explicitly registered mutations under the authenticated principal.

    Handlers must execute the complete business mutation in the caller's transaction.
    The dispatcher itself never acknowledges success; the sync repository must persist
    the business result in the same transaction before the HTTP response is returned.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, Any], DispatchContext], dict[str, Any]]] = {}

    def register(self, operation: str, handler: Callable[[dict[str, Any], DispatchContext], dict[str, Any]]) -> None:
        if not operation or operation in self._handlers:
            raise ValueError("operation must be unique and non-empty")
        self._handlers[operation] = handler

    def dispatch(self, operation: str, payload: dict[str, Any], context: DispatchContext) -> dict[str, Any]:
        handler = self._handlers.get(operation)
        if handler is None:
            raise SyncOperationNotSupported(operation)
        return handler(payload, context)

    def supported_operations(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))
