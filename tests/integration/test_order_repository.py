"""Integration coverage for the transactional order repository adapter."""

import os
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.domain.contracts import Money
from src.domain.order import Order, OrderState
from src.infrastructure.database.models import Base, StoreModel
from src.infrastructure.database.order_repository import SqlAlchemyOrderRepository


@pytest.fixture()
def database_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is required for database integration tests")
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_order_repository_round_trip_and_store_isolation(database_engine):
    with database_engine.begin() as connection:
        connection.execute(
            StoreModel.__table__.insert(),
            [
                {"id": "store-a", "tenant_id": "tenant-1", "name": "A"},
                {"id": "store-b", "tenant_id": "tenant-1", "name": "B"},
            ],
        )

    order = Order("order-1", Money(Decimal("125.50")), OrderState.PENDING)
    with Session(database_engine) as session, session.begin():
        repository = SqlAlchemyOrderRepository(session, store_id="store-a")
        repository.save(order)

    with Session(database_engine) as session:
        repository = SqlAlchemyOrderRepository(session, store_id="store-a")
        assert repository.get("order-1") == order

    with Session(database_engine) as session:
        other_store = SqlAlchemyOrderRepository(session, store_id="store-b")
        assert other_store.get("order-1") is None
