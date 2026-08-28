import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any

from app.core.database import get_db
from app.synthetic.generator import SyntheticFinancialDataEngine
from app.synthetic.seeder import DatabaseSeeder
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.anomaly.detector import IsolationForestAnomalyDetector
from app.ai.investigator import FinancialAIInvestigator
from app.models.schema import ReconciliationResult, ReconciliationStatus

router = APIRouter(prefix="/demo", tags=["Demo Mode"])


class DemoLoadResponse(BaseModel):
    status: str = "success"
    num_clusters: int = 1000
    records_loaded: int = 1000
    reconciled_count: int = 1000
    anomalies_detected: int = 0
    investigations_preloaded: int = 0
    duration_ms: float = 0.0
    summary: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


@router.post("/load", response_model=DemoLoadResponse)
def load_demo_dataset(
    num_clusters: int = Query(1000, ge=50, le=5000),
    seed: int = Query(42),
    preload_ai: bool = Query(True, description="Pre-generate AI investigations for exceptions"),
    db: Session = Depends(get_db)
):
    """
    One-Click Demo Loader:
    1. Generates 1,000 deterministic financial clusters (10 realistic ground-truth scenarios).
    2. Seeds database tables cleanly.
    3. Executes deterministic reconciliation pipeline.
    4. Executes Scikit-Learn Isolation Forest anomaly detection.
    5. Optionally pre-investigates notable exceptions with Groq AI for instant judge inspection.
    """
    t0 = time.perf_counter()

    # 1. Generate synthetic dataset
    engine = SyntheticFinancialDataEngine(seed=seed)
    dataset = engine.generate_dataset(num_clusters=num_clusters)

    # 2. Seed database
    DatabaseSeeder.seed(db=db, dataset=dataset, clear_existing=True)

    # 3. Run reconciliation
    rec_engine = DeterministicReconciliationEngine()
    rec_res = rec_engine.reconcile_all(db=db, clear_existing=True)

    # 4. Run ML Anomaly Detection
    anom_detector = IsolationForestAnomalyDetector(random_state=seed)
    anom_res = anom_detector.run_detection(db=db, clear_existing=True)

    # 5. Pre-run AI on sample exceptions for instant demo experience
    investigations_count = 0
    if preload_ai:
        investigator = FinancialAIInvestigator()
        exceptions = db.query(ReconciliationResult).filter(
            ReconciliationResult.status != ReconciliationStatus.MATCHED
        ).limit(10).all()

        for ex in exceptions:
            try:
                investigator.investigate(reconciliation_id=ex.id, db=db)
                investigations_count += 1
            except Exception:
                pass

    total_duration_ms = (time.perf_counter() - t0) * 1000.0

    return DemoLoadResponse(
        status="success",
        num_clusters=num_clusters,
        records_loaded=len(dataset["payments"]),
        reconciled_count=rec_res.processed_count,
        anomalies_detected=anom_res.anomalies_found,
        investigations_preloaded=investigations_count,
        duration_ms=round(total_duration_ms, 2),
        summary={
            "match_rate": f"{rec_res.summary.match_rate_percentage}%",
            "matched_count": rec_res.summary.matched_count,
            "exception_count": rec_res.summary.exception_count,
            "total_discrepancy": str(rec_res.summary.total_discrepancy_amount),
            "unresolved_amount": str(rec_res.summary.total_unresolved_amount),
            "anomalies_count": anom_res.anomalies_found,
        },
    )
