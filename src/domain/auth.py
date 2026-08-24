"""Authorization primitives independent of transport/persistence."""

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    INVENTORY = "inventory"
    AUDITOR = "auditor"


@dataclass(frozen=True)
class Principal:
    user_id: str
    tenant_id: str
    store_id: str
    roles: frozenset[Role]

    def require(self, *allowed: Role) -> None:
        if not self.roles.intersection(allowed):
            raise PermissionError("Insufficient role")
