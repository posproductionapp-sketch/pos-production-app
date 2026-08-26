import os
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app, get_session
from src.domain.auth import Role
from src.infrastructure.database.auth import AuthService
from src.infrastructure.database.models import Base, StoreModel


def test_checkout_refund_and_shift_flow():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def register_now(dbapi_connection, _):
        dbapi_connection.create_function(
            "now", 0, lambda: datetime.now(timezone.utc).isoformat(sep=" ")
        )

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    secret = "x" * 32

    with factory() as session:
        session.add(
            StoreModel(
                id="store",
                tenant_id="tenant",
                name="Test Store",
                created_at=datetime.now(timezone.utc),
            )
        )
        session.flush()
        AuthService(session, secret).create_user(
            tenant_id="tenant",
            store_id="store",
            username="manager",
            password="correct horse battery staple",
            roles={Role.ADMIN, Role.MANAGER, Role.CASHIER, Role.INVENTORY},
        )
        session.commit()

    previous_secret = os.environ.get("AUTH_SECRET")
    os.environ["AUTH_SECRET"] = secret

    def override_session():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    try:
        client = TestClient(app)
        login = client.post(
            "/v1/auth/login",
            json={
                "tenant_id": "tenant",
                "username": "manager",
                "password": "correct horse battery staple",
            },
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        opened = client.post("/v1/shifts/open", headers=headers, json={"opening_cash": "100.00"})
        assert opened.status_code == 200
        assert opened.json()["state"] == "open"

        variant = client.post(
            "/v1/catalog/variants",
            headers=headers,
            json={
                "product_name": "Coffee",
                "sku": "COFFEE-001",
                "description": "Hot coffee",
                "price": "50.00",
                "currency": "THB",
            },
        )
        assert variant.status_code == 200
        variant_id = variant.json()["variant_id"]

        received = client.post(
            "/v1/inventory/receive",
            headers=headers,
            json={
                "variant_id": variant_id,
                "quantity": "2",
                "correlation_id": "receipt-1",
            },
        )
        assert received.status_code == 200
        assert received.json()["quantity"] == "2"

        sale_payload = {
            "items": [{"variant_id": variant_id, "quantity": "1"}],
            "payment_method": "cash",
            "payment_reference": "cash-1",
        }
        sale = client.post(
            "/v1/sales",
            headers={**headers, "Idempotency-Key": "sale-1"},
            json=sale_payload,
        )
        assert sale.status_code == 200
        sale_body = sale.json()
        assert sale_body["state"] == "paid"
        assert sale_body["total"] == "50.00"

        duplicate = client.post(
            "/v1/sales",
            headers={**headers, "Idempotency-Key": "sale-1"},
            json=sale_payload,
        )
        assert duplicate.status_code == 200
        assert duplicate.json()["duplicate"] is True
        assert duplicate.json()["order_id"] == sale_body["order_id"]

        refund = client.post(
            "/v1/refunds",
            headers={**headers, "Idempotency-Key": "refund-1"},
            json={
                "payment_id": sale_body["payment_id"],
                "amount": "50.00",
                "provider_reference": "refund-1",
                "restock": True,
                "correlation_id": "refund-1",
            },
        )
        assert refund.status_code == 200
        assert refund.json()["amount"] == "50.00"

        closed = client.post(
            "/v1/shifts/close",
            headers=headers,
            json={"closing_cash": "100.00"},
        )
        assert closed.status_code == 200
        assert closed.json()["state"] == "closed"
    finally:
        app.dependency_overrides.clear()
        if previous_secret is None:
            os.environ.pop("AUTH_SECRET", None)
        else:
            os.environ["AUTH_SECRET"] = previous_secret
        engine.dispose()
