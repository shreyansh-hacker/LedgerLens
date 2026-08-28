import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, get_db, SessionLocal
from app.models.schema import Payment, ReconciliationResult, AnomalyResult


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def test_demo_status_endpoint(client):
    res = client.get("/api/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_initialized" in data
    assert "total_records" in data
    assert data["demo_version"] == "v1.0"
    assert data["seed"] == 42


def test_demo_load_and_idempotency(client):
    # 1. First Load (Force reset with 100 clusters for fast test execution)
    res1 = client.post("/api/demo/load?num_clusters=100&seed=42&force_reset=true&preload_ai=true")
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["status"] == "success"
    assert d1["num_clusters"] == 100
    assert d1["records_loaded"] == 100
    assert d1["cached"] is False
    assert d1["reconciled_count"] == 100

    # 2. Second Load (Idempotent call without force_reset)
    res2 = client.post("/api/demo/load?num_clusters=100&seed=42&force_reset=false")
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["status"] == "success"
    assert d2["cached"] is True
    assert d2["records_loaded"] == 100  # Zero duplicate records!


def test_demo_featured_cases(client):
    res = client.get("/api/demo/featured")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) >= 1
    for c in cases:
        assert "reconciliation_id" in c
        assert "headline" in c
        assert "classification" in c
        assert "system_confidence" in c


def test_demo_reset_database(client):
    res = client.post("/api/demo/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    status_res = client.get("/api/demo/status")
    assert status_res.status_code == 200
    assert status_res.json()["is_initialized"] is False
    assert status_res.json()["total_records"] == 0
