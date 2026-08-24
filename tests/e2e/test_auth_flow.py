import os
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from src.api.main import app, get_session
from src.infrastructure.database.auth import AuthService
from src.infrastructure.database.models import Base, StoreModel
from src.domain.auth import Role


def test_login_and_protected_me_flow():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def register_now(dbapi_connection, _):
        dbapi_connection.create_function("now", 0, lambda: datetime.now(timezone.utc).isoformat(sep=" "))

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    secret = "x" * 32
    with factory() as session:
        session.add(StoreModel(id="store", tenant_id="tenant", name="Test", created_at=datetime.now(timezone.utc)))
        session.flush()
        user = AuthService(session, secret).create_user(
            tenant_id="tenant", store_id="store", username="cashier", password="correct horse battery staple", roles={Role.CASHIER}
        )
        user.created_at = datetime.now(timezone.utc)
        session.commit()

    previous_secret = os.environ.get("AUTH_SECRET")
    os.environ["AUTH_SECRET"] = secret
    app.dependency_overrides[get_session] = lambda: (session for session in [factory()])
    try:
        client = TestClient(app)
        login = client.post("/v1/auth/login", json={"tenant_id": "tenant", "username": "cashier", "password": "correct horse battery staple"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        me = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["store_id"] == "store"
    finally:
        app.dependency_overrides.clear()
        if previous_secret is None:
            os.environ.pop("AUTH_SECRET", None)
        else:
            os.environ["AUTH_SECRET"] = previous_secret
        engine.dispose()
