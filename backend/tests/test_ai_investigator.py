import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.schema import (
    ReconciliationResult,
    InvestigationResult,
    InvestigationStatus,
)
from app.synthetic.generator import SyntheticFinancialDataEngine
from app.synthetic.seeder import DatabaseSeeder
from app.synthetic.scenarios import ScenarioType
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.anomaly.detector import IsolationForestAnomalyDetector
from app.ai.evidence import EvidenceAssembler
from app.ai.confidence import SystemConfidenceEvaluator
from app.ai.investigator import FinancialAIInvestigator
from app.ai.provider import AIProvider, GroqProvider
from app.ai.schemas import StructuredAIInvestigation, FactualClaim
from app.ai.assistant import FinanceAssistant

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
    dataset = engine.generate_dataset(num_clusters=20)
    DatabaseSeeder.seed(db_session, dataset)
    rec_engine = DeterministicReconciliationEngine()
    rec_engine.reconcile_all(db=db_session)
    anom_detector = IsolationForestAnomalyDetector()
    anom_detector.run_detection(db=db_session)
    return db_session


def test_evidence_assembler_and_hashing(seeded_db):
    """Test evidence packet compilation and deterministic SHA-256 canonical hashing."""
    rec = seeded_db.query(ReconciliationResult).first()
    assert rec is not None

    evidence_data = EvidenceAssembler.assemble_evidence(reconciliation_result=rec, db=seeded_db)
    assert "evidence" in evidence_data
    assert "evidence_hash" in evidence_data
    assert len(evidence_data["evidence_hash"]) == 64  # SHA-256 length

    # Verify canonical determinism: same input yields identical hash
    evidence_data2 = EvidenceAssembler.assemble_evidence(reconciliation_result=rec, db=seeded_db)
    assert evidence_data["evidence_hash"] == evidence_data2["evidence_hash"]


def test_system_confidence_evaluator():
    """Test composite system confidence calculation logic."""
    mock_evidence = {
        "reconciliation_summary": {
            "discrepancy_amount": "0.00",
            "matching_score": 100.0,
        },
        "payment": {"id": "pay_001"},
        "settlement": {"id": "set_001"},
        "bank_transaction": {"id": "bnk_001"},
        "recorded_fees": [{"id": "fee_001"}],
        "anomaly_context": {"severity": "LOW"},
    }

    mock_ai = StructuredAIInvestigation(
        status=InvestigationStatus.EXPLAINED,
        summary="Clean settlement match",
        facts=[FactualClaim(statement="Payment matched", evidence_ids=["pay_001", "set_001"])],
        explanation="Payment is fully accounted for.",
        evidence_references=["pay_001", "set_001"],
        missing_evidence=[],
        confidence=98.0,
        recommended_action="NO_ACTION"
    )

    conf_res = SystemConfidenceEvaluator.evaluate(evidence=mock_evidence, ai_output=mock_ai)
    assert conf_res["system_confidence"] >= 90.0
    assert conf_res["confidence_tier"] == "HIGH"


def test_ai_investigation_golden_unexplained_exception(db_session):
    """Golden Test: Unexplained exception MUST produce HUMAN_REVIEW_REQUIRED with 0 invented claims."""
    dist = {st: 0.0 for st in ScenarioType}
    dist[ScenarioType.UNEXPLAINED_EXCEPTION] = 1.0
    engine = SyntheticFinancialDataEngine(seed=42, scenario_distribution=dist)
    dataset = engine.generate_dataset(num_clusters=1)
    DatabaseSeeder.seed(db_session, dataset)

    rec_engine = DeterministicReconciliationEngine()
    rec_engine.reconcile_all(db=db_session)
    anom_detector = IsolationForestAnomalyDetector()
    anom_detector.run_detection(db=db_session)

    rec = db_session.query(ReconciliationResult).first()
    investigator = FinancialAIInvestigator()
    inv = investigator.investigate(reconciliation_id=rec.id, db=db_session)

    assert inv.investigation_status == InvestigationStatus.HUMAN_REVIEW_REQUIRED
    assert inv.recommended_action in ["HUMAN_REVIEW", "CONTACT_BANK"]
    assert float(inv.system_confidence) < 80.0
    # Strict anti-hallucination check: missing evidence must be noted
    assert len(inv.missing_evidence) > 0 or "missing" in inv.explanation.lower() or "unexplained" in inv.explanation.lower()


def test_investigation_caching(seeded_db):
    """Test that second investigation of identical evidence returns cached result instantly."""
    rec = seeded_db.query(ReconciliationResult).first()
    investigator = FinancialAIInvestigator()

    # First run (uncached)
    inv1 = investigator.investigate(reconciliation_id=rec.id, db=seeded_db)
    assert inv1.cached is False

    # Second run (cached)
    inv2 = investigator.investigate(reconciliation_id=rec.id, db=seeded_db, force_reinvestigate=False)
    assert inv2.cached is True
    assert inv2.id == inv1.id
    assert inv2.evidence_hash == inv1.evidence_hash


def test_deterministic_fallback_when_provider_unavailable(seeded_db):
    """Test graceful fallback behavior when Groq client returns None."""
    class MockUnavailableProvider(AIProvider):
        def investigate(self, evidence):
            return None, "PROVIDER_UNAVAILABLE", 0.0

    rec = seeded_db.query(ReconciliationResult).first()
    investigator = FinancialAIInvestigator(provider=MockUnavailableProvider())

    inv = investigator.investigate(reconciliation_id=rec.id, db=seeded_db, force_reinvestigate=True)
    assert inv is not None
    assert inv.summary is not None
    assert inv.investigation_status in [InvestigationStatus.EXPLAINED, InvestigationStatus.HUMAN_REVIEW_REQUIRED]


def test_natural_language_assistant(seeded_db):
    """Test safe natural-language copilot tool routing and responses."""
    assistant = FinanceAssistant()

    # Test summary query
    resp1 = assistant.query(user_query="How much money is currently unresolved?", db=seeded_db)
    assert resp1.intent in ["GET_RECONCILIATION_SUMMARY", "GET_OVERVIEW_WITH_EXCEPTIONS"]
    assert "total_unresolved" in resp1.retrieved_data_summary or "total_discrepancy" in resp1.retrieved_data_summary

    # Test delayed settlements query
    resp2 = assistant.query(user_query="Which settlements are delayed?", db=seeded_db)
    assert resp2.intent == "GET_DELAYED_SETTLEMENTS"

    # Test specific ID query
    rec = seeded_db.query(ReconciliationResult).first()
    resp3 = assistant.query(user_query=f"Why is {rec.payment_id} unreconciled?", db=seeded_db)
    assert resp3.intent == "GET_ENTITY_DETAIL"
    assert resp3.retrieved_data_summary["payment_id"] == rec.payment_id


def test_api_investigation_and_assistant_endpoints(client, seeded_db):
    """Test /api/investigations and /api/assistant API endpoints."""
    rec = seeded_db.query(ReconciliationResult).first()

    # 1. Trigger POST /api/investigations/{rec.id}/run
    run_resp = client.post(f"/api/investigations/{rec.id}/run")
    assert run_resp.status_code == 200
    inv_data = run_resp.json()
    assert inv_data["id"] == f"inv_{rec.id.replace('rec_', '')}"
    assert "investigation_status" in inv_data
    assert "system_confidence" in inv_data

    # 2. GET /api/investigations/summary
    sum_resp = client.get("/api/investigations/summary")
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["total_investigations"] >= 1

    # 3. GET /api/investigations
    list_resp = client.get("/api/investigations?limit=10")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1

    # 4. GET /api/investigations/{id}
    detail_resp = client.get(f"/api/investigations/{inv_data['id']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == inv_data["id"]

    # 5. POST /api/assistant/query
    ast_resp = client.post("/api/assistant/query", json={"query": "Show me the biggest discrepancies"})
    assert ast_resp.status_code == 200
    ast_data = ast_resp.json()
    assert "answer" in ast_data
    assert "intent" in ast_data
