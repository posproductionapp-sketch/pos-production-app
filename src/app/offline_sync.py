"""Deterministic offline command replay with idempotency semantics."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SyncCommand:
    command_id: str
    operation: str
    payload: dict


class OfflineSyncService:
    def __init__(self, execute: Callable[[SyncCommand], object], seen: set[str] | None = None) -> None:
        self.execute = execute
        self.seen = seen if seen is not None else set()

    def replay(self, commands: list[SyncCommand]) -> list[object]:
        results = []
        for command in commands:
            if command.command_id in self.seen:
                continue
            result = self.execute(command)
            self.seen.add(command.command_id)
            results.append(result)
        return results
