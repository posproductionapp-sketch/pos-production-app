"""Regression coverage for the shift lifecycle invariant on PostgreSQL."""

import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import Base, StoreModel
from src.infrastructure.database.shift_models import ShiftModel
from src.infrastructure.database.shifts import ShiftRepository


@pytest.fixture()
def engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is required")
    if not url.startswith(("postgresql://", "postgresql+psycopg://")):
        pytest.skip("PostgreSQL is required for shift concurrency certification")
    value = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(value)
    try:
        yield value
    finally:
        Base.metadata.drop_all(value)
        value.dispose()


def test_multiple_closed_shifts_are_preserved(engine):
    with Session(engine) as session, session.begin():
        session.add(StoreModel(id="shift-store", tenant_id="shift-tenant", name="Shift Store"))
    with Session(engine) as session, session.begin():
        repo = ShiftRepository(session, tenant_id="shift-tenant", store_id="shift-store")
        first = repo.open(actor_id="u1", opening_cash=Decimal("100"))
        repo.close(actor_id="u1", closing_cash=Decimal("110"))
        second = repo.open(actor_id="u2", opening_cash=Decimal("200"))
        repo.close(actor_id="u2", closing_cash=Decimal("220"))
    with Session(engine) as session:
        closed = session.scalars(select(ShiftModel).where(ShiftModel.store_id == "shift-store", ShiftModel.state == "closed").order_by(ShiftModel.opened_at)).all()
        assert [shift.id for shift in closed] == [first.id, second.id]
        assert [shift.closing_cash for shift in closed] == [Decimal("110.00"), Decimal("220.00")]


def _try_open(engine, actor_id: str):
    with Session(engine) as session, session.begin():
        try:
            shift = ShiftRepository(session, tenant_id="concurrent-tenant", store_id="concurrent-store").open(actor_id=actor_id, opening_cash=Decimal("0"))
            return ("opened", shift.id)
        except ValueError as exc:
            return ("rejected", str(exc))


def test_concurrent_open_attempts_leave_exactly_one_open_shift(engine):
    with Session(engine) as session, session.begin():
        session.add(StoreModel(id="concurrent-store", tenant_id="concurrent-tenant", name="Concurrent Store"))
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda actor: _try_open(engine, actor), ["u1", "u2"]))
    assert sorted(result[0] for result in results) == ["opened", "rejected"]
    with Session(engine) as session:
        open_shifts = session.scalars(select(ShiftModel).where(ShiftModel.store_id == "concurrent-store", ShiftModel.state == "open")).all()
        assert len(open_shifts) == 1
