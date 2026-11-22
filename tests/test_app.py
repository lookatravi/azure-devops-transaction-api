from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_success(monkeypatch):
    monkeypatch.delenv("SIMULATE_OUTAGE", raising=False)
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_readiness_failure(monkeypatch):
    monkeypatch.setenv("SIMULATE_OUTAGE", "true")
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"


def test_demo_transaction():
    response = client.get("/api/v1/transactions/demo-001")
    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


def test_unknown_transaction_returns_404():
    assert client.get("/api/v1/transactions/unknown").status_code == 404
