import os
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.infrastructure.database.models import Base, StoreModel, ProductModel, ProductVariantModel, OrderModel
from src.infrastructure.database.inventory import InventoryInsufficientStock, SqlAlchemyInventoryRepository
from src.infrastructure.database.payment import RefundExceedsPayment, SqlAlchemyPaymentRepository, SqlAlchemyRefundRepository


@pytest.fixture()
def engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is required")
    value = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(value)
    try:
        yield value
    finally:
        with value.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(text(f'DELETE FROM "{table.name}"'))
        value.dispose()


def seed_catalog(session: Session) -> None:
    session.add(StoreModel(id="s", tenant_id="t", name="Store"))
    session.flush()
    session.add(ProductModel(id="p", store_id="s", name="Product"))
    session.flush()
    session.add(ProductVariantModel(id="v", store_id="s", product_id="p", sku="SKU"))
    session.flush()


def test_inventory_never_goes_negative(engine):
    with Session(engine) as session, session.begin():
        seed_catalog(session)
    with Session(engine) as session, session.begin():
        repository = SqlAlchemyInventoryRepository(session, store_id="s")
        assert repository.adjust(variant_id="v", delta=Decimal("5"), reason="receipt", correlation_id="c1") == Decimal("5")
        with pytest.raises(InventoryInsufficientStock):
            repository.adjust(variant_id="v", delta=Decimal("-6"), reason="sale", correlation_id="c2")


def test_refund_cannot_exceed_payment(engine):
    with Session(engine) as session, session.begin():
        seed_catalog(session)
        session.add(OrderModel(id="o", store_id="s", state="pending", total_amount=Decimal("100"), currency="THB"))
    with Session(engine) as session, session.begin():
        payment = SqlAlchemyPaymentRepository(session).record(order_id="o", provider="test", provider_reference="pay-1", amount=Decimal("100"), currency="THB", state="captured")
        refunds = SqlAlchemyRefundRepository(session)
        refunds.record(payment_id=payment.id, amount=Decimal("60"), currency="THB", state="completed", provider_reference="ref-1")
        with pytest.raises(RefundExceedsPayment):
            refunds.record(payment_id=payment.id, amount=Decimal("50"), currency="THB", state="completed", provider_reference="ref-2")
