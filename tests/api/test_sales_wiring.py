"""Regression tests for the live sales HTTP path and financial invariants."""

from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.api.main import app, get_session, principal
from src.infrastructure.database.models import Base, InventoryBalanceModel, OrderItemModel, OrderModel, PaymentModel, PriceModel, ProductModel, ProductVariantModel, StoreModel


def _principal():
    def require(*_roles):
        return None
    return SimpleNamespace(user_id="u", tenant_id="t", store_id="s", roles=set(), require=require)


def test_live_sales_path_uses_checkout_vat_discount_and_idempotency(monkeypatch):
    monkeypatch.setenv("VAT_RATE", "0.07")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        session.add(StoreModel(id="s", tenant_id="t", name="Store"))
        session.add(ProductModel(id="p", store_id="s", name="Coffee"))
        session.add(ProductVariantModel(id="v", store_id="s", product_id="p", sku="SKU", description="Drink"))
        session.add(PriceModel(id="price", store_id="s", variant_id="v", amount=Decimal("100"), currency="THB"))
        session.add(InventoryBalanceModel(id="stock", store_id="s", variant_id="v", quantity=Decimal("10")))

    with Session(engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        app.dependency_overrides[principal] = _principal
        client = TestClient(app)
        payload = {"items": [{"variant_id": "v", "quantity": "1"}], "payment_method": "card", "payment_reference": "pay-1", "discount_rate": "0.10"}
        headers = {"Idempotency-Key": "sale-test-1"}
        response = client.post("/v1/sales", json=payload, headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["subtotal"] == "100.00"
        assert body["discount"] == "10.00"
        assert body["tax"] == "6.30"
        assert body["total"] == "96.30"
        assert body["duplicate"] is False

        duplicate = client.post("/v1/sales", json=payload, headers=headers)
        assert duplicate.status_code == 200
        assert duplicate.json()["duplicate"] is True
        assert duplicate.json()["order_id"] == body["order_id"]

        order = session.get(OrderModel, body["order_id"])
        item = session.scalar(select(OrderItemModel).where(OrderItemModel.order_id == body["order_id"]))
        stock = session.get(InventoryBalanceModel, "stock")
        assert order is not None and order.total_amount == Decimal("96.30")
        assert item is not None and item.tax_amount == Decimal("6.30") and item.discount_amount == Decimal("10.00")
        assert stock is not None and stock.quantity == Decimal("9.000")
    app.dependency_overrides.clear()


def test_refund_rejects_payment_from_another_tenant_or_store():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        session.add_all([
            StoreModel(id="s", tenant_id="t", name="Current Store"),
            StoreModel(id="other-store", tenant_id="other-tenant", name="Other Store"),
            OrderModel(id="other-order", store_id="other-store", state="paid", total_amount=Decimal("100.00"), currency="THB"),
            PaymentModel(id="other-payment", order_id="other-order", provider="card", provider_reference="other-pay-1", amount=Decimal("100.00"), currency="THB", state="captured"),
        ])

    with Session(engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        app.dependency_overrides[principal] = _principal
        client = TestClient(app)
        response = client.post(
            "/v1/refunds",
            json={
                "payment_id": "other-payment",
                "amount": "10.00",
                "provider_reference": "refund-1",
                "restock": False,
                "correlation_id": "refund-test-1",
            },
            headers={"Idempotency-Key": "refund-test-1"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"
        assert session.query(PaymentModel).filter(PaymentModel.id == "other-payment").count() == 1
        assert session.execute(select(PaymentModel).where(PaymentModel.id == "other-payment")).scalar_one().amount == Decimal("100.00")
    app.dependency_overrides.clear()
