from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from app.core.database import get_db
from app.models.schema import (
    AnomalyResult,
    ReconciliationResult,
    Payment,
    Order,
    Merchant,
    AnomalySeverity,
)
from app.anomaly.detector import IsolationForestAnomalyDetector
from app.anomaly.schemas import (
    AnomalyRunRequest,
    AnomalyRunResult,
    AnomalySummaryResponse,
    AnomalyItemResponse,
)

router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])


@router.post("/run", response_model=AnomalyRunResult)
def run_anomaly_detection(
    req: AnomalyRunRequest = AnomalyRunRequest(),
    db: Session = Depends(get_db)
):
    """
    Executes population-level feature extraction and Isolation Forest anomaly scoring.
    """
    detector = IsolationForestAnomalyDetector(
        contamination=req.contamination,
        n_estimators=req.n_estimators,
        random_state=req.random_state,
        high_severity_threshold=req.high_severity_threshold,
        medium_severity_threshold=req.medium_severity_threshold,
    )
    result = detector.run_detection(db=db, clear_existing=True)
    return result


@router.get("/summary", response_model=AnomalySummaryResponse)
def get_anomaly_summary(
    db: Session = Depends(get_db)
):
    """
    Retrieves high-level anomaly metrics and severity distribution.
    """
    return IsolationForestAnomalyDetector.compute_summary(db=db)


@router.get("/results", response_model=List[AnomalyItemResponse])
def get_anomaly_results(
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH)"),
    is_anomaly: Optional[bool] = Query(None, description="Filter by anomaly flag"),
    min_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum normalized score"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lists paginated anomaly detection results with multi-criteria filtering.
    """
    query = db.query(AnomalyResult).join(
        ReconciliationResult, AnomalyResult.reconciliation_id == ReconciliationResult.id
    ).join(
        Payment, ReconciliationResult.payment_id == Payment.id, isouter=True
    )

    if severity:
        query = query.filter(AnomalyResult.severity == severity.upper())
    if is_anomaly is not None:
        query = query.filter(AnomalyResult.is_anomaly == is_anomaly)
    if min_score is not None:
        query = query.filter(AnomalyResult.normalized_score >= Decimal(str(min_score)))

    results = query.order_by(AnomalyResult.normalized_score.desc()).offset(offset).limit(limit).all()

    items: List[AnomalyItemResponse] = []
    for a in results:
        rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == a.reconciliation_id).first()
        payment = db.query(Payment).filter(Payment.id == rec.payment_id).first() if rec else None
        order = db.query(Order).filter(Order.id == rec.order_id).first() if (rec and rec.order_id) else None
        merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first() if order else None

        items.append(AnomalyItemResponse(
            id=a.id,
            reconciliation_id=a.reconciliation_id,
            payment_id=rec.payment_id if rec else "unknown",
            order_reference=order.order_reference if order else None,
            payment_reference=payment.payment_reference if payment else None,
            merchant_id=merchant.id if merchant else None,
            merchant_name=merchant.name if merchant else None,
            payment_amount=payment.amount if payment else Decimal("0.00"),
            discrepancy_amount=rec.discrepancy_amount if rec else Decimal("0.00"),
            reconciliation_status=rec.status if rec else "MATCHED",
            reconciliation_classification=rec.classification if rec else "NONE",
            raw_anomaly_score=float(a.raw_anomaly_score),
            normalized_score=float(a.normalized_score),
            severity=a.severity,
            is_anomaly=a.is_anomaly,
            detected_features=a.detected_features or {},
            explanation_signals=a.explanation_signals or [],
            model_version=a.model_version,
            created_at=a.created_at,
        ))

    return items


@router.get("/results/{result_id}", response_model=AnomalyItemResponse)
def get_anomaly_result_by_id(
    result_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves single detailed anomaly result by ID.
    """
    a = db.query(AnomalyResult).filter(AnomalyResult.id == result_id).first()
    if not a:
        raise HTTPException(status_code=404, detail=f"Anomaly result '{result_id}' not found.")

    rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == a.reconciliation_id).first()
    payment = db.query(Payment).filter(Payment.id == rec.payment_id).first() if rec else None
    order = db.query(Order).filter(Order.id == rec.order_id).first() if (rec and rec.order_id) else None
    merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first() if order else None

    return AnomalyItemResponse(
        id=a.id,
        reconciliation_id=a.reconciliation_id,
        payment_id=rec.payment_id if rec else "unknown",
        order_reference=order.order_reference if order else None,
        payment_reference=payment.payment_reference if payment else None,
        merchant_id=merchant.id if merchant else None,
        merchant_name=merchant.name if merchant else None,
        payment_amount=payment.amount if payment else Decimal("0.00"),
        discrepancy_amount=rec.discrepancy_amount if rec else Decimal("0.00"),
        reconciliation_status=rec.status if rec else "MATCHED",
        reconciliation_classification=rec.classification if rec else "NONE",
        raw_anomaly_score=float(a.raw_anomaly_score),
        normalized_score=float(a.normalized_score),
        severity=a.severity,
        is_anomaly=a.is_anomaly,
        detected_features=a.detected_features or {},
        explanation_signals=a.explanation_signals or [],
        model_version=a.model_version,
        created_at=a.created_at,
    )
