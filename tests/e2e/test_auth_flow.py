from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.main import app, get_session
from src.infrastructure.database.auth import AuthService
from src.infrastructure.database.models import Base, StoreModel
from src.domain.auth import Role


def test_login_and_protected_me_flow():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    with factory() as session:
        session.add(StoreModel(id="store", tenant_id="tenant", name="Test"))
        session.flush()
        AuthService(session, "x" * 32).create_user(
            tenant_id="tenant", store_id="store", username="cashier", password="correct horse battery staple", roles={Role.CASHIER}
        )
        session.commit()

    def override_session():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
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
        engine.dispose()
