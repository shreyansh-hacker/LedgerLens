import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.schema import (
    Merchant,
    Order,
    Payment,
    Fee,
    Tax,
    Refund,
    Settlement,
    BankTransaction,
    ReconciliationResult,
    ReconciliationStatus,
)
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.synthetic.generator import SyntheticFinancialDataEngine
from app.synthetic.seeder import DatabaseSeeder
from app.synthetic.scenarios import ScenarioType

# In-memory test database fixture with StaticPool for thread-safe cross-connection testing
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


def test_normal_match_reconciliation(db_session):
    """Test that a clean normal transaction reconciles to MATCHED with zero discrepancy."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.NORMAL_MATCH] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=10)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.processed_count == 10
    assert result.summary.matched_count == 10
    assert result.summary.exception_count == 0
    assert result.summary.match_rate_percentage == 100.0
    assert result.summary.total_discrepancy_amount == Decimal("0.00")

    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.MATCHED
        assert r.classification == "NONE"
        assert r.discrepancy_amount == Decimal("0.00")
        assert r.evidence_payload["calculation"]["expected_net_settlement"] == r.evidence_payload["calculation"]["actual_bank_credit"]


def test_fee_mismatch_reconciliation(db_session):
    """Test that unexpected settlement fees are classified as FEE_MISMATCH."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.FEE_MISMATCH] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.exception_count == 5
    assert result.summary.matched_count == 0
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.EXCEPTION
        assert r.classification == "FEE_MISMATCH"
        assert r.discrepancy_amount > Decimal("0.00")


def test_tax_mismatch_reconciliation(db_session):
    """Test that GST calculation variance is classified as TAX_MISMATCH."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.TAX_MISMATCH] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.exception_count == 5
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.EXCEPTION
        assert r.classification == "TAX_MISMATCH"


def test_missing_bank_reconciliation(db_session):
    """Test missing bank transactions are flagged as MISSING_BANK_TRANSACTION."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.MISSING_BANK_TRANSACTION] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.missing_bank_count == 5
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.MISSING_BANK_TRANSACTION
        assert r.classification == "MISSING_BANK_TRANSACTION"
        assert r.actual_bank_amount is None


def test_missing_settlement_reconciliation(db_session):
    """Test missing settlements are flagged as MISSING_SETTLEMENT."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.MISSING_SETTLEMENT] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.missing_settlement_count == 5
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.MISSING_SETTLEMENT
        assert r.classification == "MISSING_SETTLEMENT"
        assert r.actual_settlement_amount is None


def test_duplicate_settlement_reconciliation(db_session):
    """Test double settlement entries are flagged as DUPLICATE."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.DUPLICATE_SETTLEMENT] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.duplicate_count == 5
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.DUPLICATE
        assert r.classification == "DUPLICATE_SETTLEMENT"


def test_reference_discrepancy_reconciliation(db_session):
    """Test reference ID discrepancies are matched via proximity and classified as REFERENCE_ID_DISCREPANCY."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.REFERENCE_ID_DISCREPANCY] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.classification == "REFERENCE_ID_DISCREPANCY"
        assert r.matching_method == "AMOUNT_PROXIMITY"
        assert r.matching_score == Decimal("85.00")


def test_settlement_delay_reconciliation(db_session):
    """Test that settlements beyond SLA threshold are marked MATCHED with operational warning."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.SETTLEMENT_DELAY] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine(sla_delay_threshold_days=7)
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.matched_count == 5
    assert result.summary.operational_warnings_count == 5
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.MATCHED
        assert r.operational_warning == "SETTLEMENT_DELAY"
        assert r.classification == "SETTLEMENT_DELAY"


def test_unexplained_exception_reconciliation(db_session):
    """Test unrecorded deductions are classified as UNEXPLAINED_EXCEPTION."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.UNEXPLAINED_EXCEPTION] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=5)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    result = rec_engine.reconcile_all(db=db_session)

    assert result.summary.exception_count == 5
    assert result.summary.total_unresolved_amount > Decimal("0.00")
    results = db_session.query(ReconciliationResult).all()
    for r in results:
        assert r.status == ReconciliationStatus.EXCEPTION
        assert r.classification == "UNEXPLAINED_EXCEPTION"


def test_ambiguity_rule_competing_candidates(db_session):
    """Test that ambiguous competing matches are marked REVIEW rather than picking arbitrarily."""
    # Create merchant and order
    merchant = Merchant(id="mer_test", name="Test Mer", currency="INR")
    order = Order(id="ord_test", merchant_id="mer_test", order_reference="ORD_TEST", total_amount=Decimal("5000.00"), currency="INR")
    pay = Payment(id="pay_test", order_id="ord_test", payment_reference="PAY_TEST", amount=Decimal("5000.00"), currency="INR", captured_at=datetime(2026, 7, 1, 10, 0, 0))
    fee = Fee(id="fee_test", payment_id="pay_test", fee_type="card_fee", amount=Decimal("100.00"), currency="INR")
    tax = Tax(id="tax_test", payment_id="pay_test", tax_type="GST_18", amount=Decimal("18.00"), currency="INR")

    # Two competing unlinked settlements with the exact same amount and timestamp
    set1 = Settlement(id="set_comp1", payment_id=None, settlement_reference="SET_UNLINKED_1", gross_amount=Decimal("5000.00"), fee_amount=Decimal("100.00"), tax_amount=Decimal("18.00"), net_amount=Decimal("4882.00"), currency="INR", settled_at=datetime(2026, 7, 2, 10, 0, 0))
    set2 = Settlement(id="set_comp2", payment_id=None, settlement_reference="SET_UNLINKED_2", gross_amount=Decimal("5000.00"), fee_amount=Decimal("100.00"), tax_amount=Decimal("18.00"), net_amount=Decimal("4882.00"), currency="INR", settled_at=datetime(2026, 7, 2, 11, 0, 0))

    db_session.add_all([merchant, order, pay, fee, tax, set1, set2])
    db_session.commit()

    rec_engine = DeterministicReconciliationEngine()
    rec_engine.reconcile_all(db=db_session)

    res = db_session.query(ReconciliationResult).filter(ReconciliationResult.payment_id == "pay_test").first()
    assert res.status == ReconciliationStatus.REVIEW
    assert res.matching_method == "AMBIGUOUS_COMPETING_MATCHES"
    assert len(res.evidence_payload["competing_candidates"]) == 2


def test_api_reconciliation_endpoints(client, db_session):
    """Test /api/reconciliation API endpoints."""
    # Seed 20 demo records
    engine = SyntheticFinancialDataEngine(seed=42)
    dataset = engine.generate_dataset(num_clusters=20)
    DatabaseSeeder.seed(db_session, dataset)

    # 1. Trigger POST /api/reconciliation/run
    run_resp = client.post("/api/reconciliation/run", json={"recalculate_all": True})
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["status"] == "success"
    assert run_data["processed_count"] == 20
    assert "summary" in run_data

    # 2. GET /api/reconciliation/summary
    sum_resp = client.get("/api/reconciliation/summary")
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["total_records"] == 20
    assert sum_data["match_rate_percentage"] > 0

    # 3. GET /api/reconciliation/results
    list_resp = client.get("/api/reconciliation/results?limit=10")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 10
    first_item_id = items[0]["id"]

    # 4. GET /api/reconciliation/results/{id}
    detail_resp = client.get(f"/api/reconciliation/results/{first_item_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == first_item_id
    assert "evidence_payload" in detail_data
    assert "calculation" in detail_data["evidence_payload"]
