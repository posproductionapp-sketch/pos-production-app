"""Cash shift lifecycle and reconciliation invariants."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class ShiftState(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class CashMovementType(StrEnum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"
    SALE = "sale"
    REFUND = "refund"


@dataclass(frozen=True)
class CashMovement:
    movement_id: str
    movement_type: CashMovementType
    amount: Decimal
    reason: str
    actor_id: str
    correlation_id: str

    def __post_init__(self) -> None:
        if not self.movement_id or not self.actor_id or not self.correlation_id:
            raise ValueError("Movement identifiers are required")
        if self.amount <= Decimal("0"):
            raise ValueError("Cash movement amount must be greater than zero")
        if not self.reason.strip():
            raise ValueError("Cash movement reason is required")


@dataclass(frozen=True)
class Shift:
    shift_id: str
    tenant_id: str
    store_id: str
    opened_by: str
    opening_cash: Decimal
    state: ShiftState = ShiftState.OPEN

    def __post_init__(self) -> None:
        if not self.shift_id or not self.tenant_id or not self.store_id or not self.opened_by:
            raise ValueError("Shift identifiers are required")
        if self.opening_cash < 0:
            raise ValueError("Opening cash cannot be negative")

    def close(self, closing_cash: Decimal) -> "Shift":
        if self.state is not ShiftState.OPEN:
            raise ValueError("Shift is already closed")
        if closing_cash < 0:
            raise ValueError("Closing cash cannot be negative")
        return Shift(self.shift_id, self.tenant_id, self.store_id, self.opened_by, self.opening_cash, ShiftState.CLOSED)
