from decimal import Decimal

import pytest

from src.domain.shift import CashMovement, CashMovementType, Shift, ShiftState


def test_shift_close_is_one_way():
    shift = Shift("s1", "t1", "store1", "u1", Decimal("100.00"))
    closed = shift.close(Decimal("120.00"))
    assert closed.state is ShiftState.CLOSED
    with pytest.raises(ValueError):
        closed.close(Decimal("130.00"))


def test_cash_movement_requires_positive_amount_and_audit_context():
    with pytest.raises(ValueError):
        CashMovement("m1", CashMovementType.CASH_IN, Decimal("0"), "deposit", "u1", "c1")
    movement = CashMovement("m1", CashMovementType.CASH_IN, Decimal("10"), "deposit", "u1", "c1")
    assert movement.amount == Decimal("10")
