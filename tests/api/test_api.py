from fastapi.testclient import TestClient

from src.api.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_protected_endpoint_requires_bearer_token():
    client = TestClient(app)
    response = client.get("/v1/me")
    assert response.status_code == 401
