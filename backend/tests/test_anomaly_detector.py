import pytest
from decimal import Decimal
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.schema import (
    ReconciliationResult,
    AnomalyResult,
    AnomalySeverity,
)
from app.synthetic.generator import SyntheticFinancialDataEngine
from app.synthetic.seeder import DatabaseSeeder
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.anomaly.detector import IsolationForestAnomalyDetector
from app.anomaly.features import AnomalyFeatureExtractor, FEATURE_NAMES
from app.anomaly.signals import AnomalySignalGenerator

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_db(db_session):
    engine = SyntheticFinancialDataEngine(seed=42)
    dataset = engine.generate_dataset(num_clusters=100)
    DatabaseSeeder.seed(db_session, dataset)
    rec_engine = DeterministicReconciliationEngine()
    rec_engine.reconcile_all(db=db_session)
    return db_session


def test_feature_extraction_matrix(seeded_db):
    """Test feature extraction builds correct matrix dimensions without NaN/Inf."""
    reconciliation_results = seeded_db.query(ReconciliationResult).all()
    assert len(reconciliation_results) == 100

    from app.models.schema import Payment, Order, Fee, Tax, Refund, Settlement, BankTransaction
    payments_by_id = {p.id: p for p in seeded_db.query(Payment).all()}
    orders_by_id = {o.id: o for o in seeded_db.query(Order).all()}
    fees_by_payment_id = {}
    for f in seeded_db.query(Fee).all():
        fees_by_payment_id.setdefault(f.payment_id, []).append(f)
    taxes_by_payment_id = {}
    for t in seeded_db.query(Tax).all():
        taxes_by_payment_id.setdefault(t.payment_id, []).append(t)
    refunds_by_payment_id = {}
    for r in seeded_db.query(Refund).all():
        refunds_by_payment_id.setdefault(r.payment_id, []).append(r)
    settlements_by_id = {s.id: s for s in seeded_db.query(Settlement).all()}
    bank_by_id = {b.id: b for b in seeded_db.query(BankTransaction).all()}

    matrix, feature_dicts, rec_ids = AnomalyFeatureExtractor.extract_features(
        reconciliation_results=reconciliation_results,
        payments_by_id=payments_by_id,
        orders_by_id=orders_by_id,
        fees_by_payment_id=fees_by_payment_id,
        taxes_by_payment_id=taxes_by_payment_id,
        refunds_by_payment_id=refunds_by_payment_id,
        settlements_by_id=settlements_by_id,
        bank_by_id=bank_by_id,
    )

    assert matrix.shape == (100, len(FEATURE_NAMES))
    assert not np.isnan(matrix).any()
    assert not np.isinf(matrix).any()
    assert len(feature_dicts) == 100
    assert len(rec_ids) == 100


def test_leakage_protection():
    """Verify that feature names contain zero ground-truth identifiers."""
    forbidden_tokens = ["ground_truth", "scenario", "expected_reason", "oracle", "gt_"]
    for feat in FEATURE_NAMES:
        for token in forbidden_tokens:
            assert token not in feat.lower(), f"Potential data leakage detected in feature '{feat}'"


def test_model_determinism_and_reproducibility(seeded_db):
    """Test that same random seed produces identical anomaly scores."""
    detector1 = IsolationForestAnomalyDetector(random_state=42)
    detector2 = IsolationForestAnomalyDetector(random_state=42)

    res1 = detector1.run_detection(db=seeded_db, clear_existing=True)
    scores1 = [float(r.normalized_score) for r in seeded_db.query(AnomalyResult).all()]

    res2 = detector2.run_detection(db=seeded_db, clear_existing=True)
    scores2 = [float(r.normalized_score) for r in seeded_db.query(AnomalyResult).all()]

    assert scores1 == scores2
    assert res1.summary.anomalies_detected == res2.summary.anomalies_detected


def test_score_range_and_severity_tiers(seeded_db):
    """Test normalized score bounded in [0, 100] and severity thresholds adhere to spec."""
    detector = IsolationForestAnomalyDetector(
        high_severity_threshold=70.0,
        medium_severity_threshold=40.0
    )
    result = detector.run_detection(db=seeded_db)

    assert result.status == "success"
    assert result.processed_count == 100

    records = seeded_db.query(AnomalyResult).all()
    for rec in records:
        score = float(rec.normalized_score)
        assert 0.0 <= score <= 100.0

        if score >= 70.0:
            assert rec.severity == AnomalySeverity.HIGH
        elif score >= 40.0:
            assert rec.severity == AnomalySeverity.MEDIUM
        else:
            assert rec.severity == AnomalySeverity.LOW


def test_signal_generation():
    """Test observable explanation signals generated from extreme feature values."""
    mock_features = {
        "payment_amount": 120000.0,
        "amount_ratio_to_merchant_median": 8.5,
        "fee_to_amount_ratio": 0.045,
        "tax_to_fee_ratio": 0.0,
        "discrepancy_to_amount_ratio": 0.25,
        "settlement_delay_hours": 24.0 * 20,  # 20 days
        "is_bank_missing": 1.0,
    }

    signals = AnomalySignalGenerator.generate_signals(
        features=mock_features,
        raw_score=-0.75,
        normalized_score=92.0
    )

    assert len(signals) >= 4
    signal_text = " ".join(signals)
    assert "8.5× higher" in signal_text
    assert "exceeds standard gateway" in signal_text
    assert "Zero/negligible GST" in signal_text
    assert "20.0 days" in signal_text
    assert "bank statement credit is missing" in signal_text


def test_anomaly_api_endpoints(client, seeded_db):
    """Test /api/anomalies API endpoints."""
    # 1. Trigger POST /api/anomalies/run
    run_resp = client.post("/api/anomalies/run", json={"n_estimators": 50, "contamination": 0.15})
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["status"] == "success"
    assert run_data["processed_count"] == 100
    assert "summary" in run_data

    # 2. GET /api/anomalies/summary
    sum_resp = client.get("/api/anomalies/summary")
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["total_evaluated"] == 100
    assert "severity_breakdown" in sum_data

    # 3. GET /api/anomalies/results
    list_resp = client.get("/api/anomalies/results?limit=10")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 10
    first_item_id = items[0]["id"]

    # 4. GET /api/anomalies/results/{id}
    detail_resp = client.get(f"/api/anomalies/results/{first_item_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == first_item_id
    assert "raw_anomaly_score" in detail_data
    assert "normalized_score" in detail_data
    assert "explanation_signals" in detail_data
