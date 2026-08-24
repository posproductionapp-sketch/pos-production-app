from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.infrastructure.database.models import Base, StoreModel, ProductModel, ProductVariantModel, OrderModel
from src.infrastructure.database.inventory import InventoryInsufficientStock, SqlAlchemyInventoryRepository
from src.infrastructure.database.payment import RefundExceedsPayment, SqlAlchemyPaymentRepository, SqlAlchemyRefundRepository
from src.infrastructure.database.shifts import ShiftRepository
from src.infrastructure.database import shift_models  # noqa: F401 - register shift tables with Base.metadata


@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(StoreModel(id="store-1", tenant_id="tenant-1", name="Test"))
        db.commit()
        yield db


def test_inventory_rejects_negative_stock_and_records_movements(session):
    product = ProductModel(id="product-1", store_id="store-1", name="Coffee")
    variant = ProductVariantModel(id="variant-1", store_id="store-1", product_id=product.id, sku="COFFEE", description="Coffee")
    session.add_all([product, variant])
    session.commit()
    repo = SqlAlchemyInventoryRepository(session, store_id="store-1")
    assert repo.adjust(variant_id=variant.id, delta=Decimal("10"), reason="stock_receipt", correlation_id="c1") == Decimal("10")
    assert repo.adjust(variant_id=variant.id, delta=Decimal("3"), reason="sale", correlation_id="c2") == Decimal("7")
    with pytest.raises(InventoryInsufficientStock):
        repo.adjust(variant_id=variant.id, delta=Decimal("-8"), reason="sale", correlation_id="c3")


def test_payment_and_refund_are_exact_and_capped(session):
    session.add(OrderModel(id="order-1", store_id="store-1", state="paid", total_amount=Decimal("100.00"), currency="THB"))
    session.commit()
    payment = SqlAlchemyPaymentRepository(session).record(order_id="order-1", provider="cash", provider_reference="pay-1", amount=Decimal("100.00"), currency="THB", state="captured")
    refund_repo = SqlAlchemyRefundRepository(session)
    refund_repo.record(payment_id=payment.id, amount=Decimal("40.00"), currency="THB", state="captured", provider_reference="ref-1")
    refund_repo.record(payment_id=payment.id, amount=Decimal("60.00"), currency="THB", state="captured", provider_reference="ref-2")
    with pytest.raises(RefundExceedsPayment):
        refund_repo.record(payment_id=payment.id, amount=Decimal("0.01"), currency="THB", state="captured", provider_reference="ref-3")


def test_shift_allows_only_one_open_shift_and_cash_movements(session):
    repo = ShiftRepository(session, tenant_id="tenant-1", store_id="store-1")
    shift = repo.open(actor_id="user-1", opening_cash=Decimal("500"))
    repo.add_cash_movement(shift_id=shift.id, movement_type="cash_in", amount=Decimal("50"), reason="float", actor_id="user-1", correlation_id="c1")
    with pytest.raises(ValueError):
        repo.open(actor_id="user-2", opening_cash=Decimal("500"))
    closed = repo.close(actor_id="manager-1", closing_cash=Decimal("550"))
    assert closed.state == "closed"
