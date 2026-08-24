"""Integration coverage for the transactional order repository adapter."""

import os
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text

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
        with engine.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(text(f'DELETE FROM "{table.name}"'))
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

    with database_engine.begin() as transaction:
        session = __import__("sqlalchemy.orm", fromlist=["Session"]).Session(bind=transaction)
        repository = SqlAlchemyOrderRepository(session, store_id="store-a")
        order = Order("order-1", Money(Decimal("125.50")), OrderState.PENDING)
        repository.save(order)
        session.commit()

    with database_engine.begin() as transaction:
        session = __import__("sqlalchemy.orm", fromlist=["Session"]).Session(bind=transaction)
        repository = SqlAlchemyOrderRepository(session, store_id="store-a")
        loaded = repository.get("order-1")
        assert loaded == order

    with database_engine.begin() as transaction:
        session = __import__("sqlalchemy.orm", fromlist=["Session"]).Session(bind=transaction)
        other_store = SqlAlchemyOrderRepository(session, store_id="store-b")
        assert other_store.get("order-1") is None
