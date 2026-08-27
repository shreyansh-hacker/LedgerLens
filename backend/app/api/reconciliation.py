from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from app.core.database import get_db
from app.models.schema import (
    ReconciliationResult,
    ReconciliationStatus,
    Payment,
    Order,
    Settlement,
    BankTransaction,
)
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.reconciliation.schemas import (
    ReconciliationRunRequest,
    ReconciliationRunResult,
    ReconciliationSummaryResponse,
    ReconciliationItemResponse,
)

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])


@router.post("/run", response_model=ReconciliationRunResult)
def run_reconciliation(
    req: ReconciliationRunRequest = ReconciliationRunRequest(),
    db: Session = Depends(get_db)
):
    """
    Triggers a deterministic reconciliation run across payments and statements in the database.
    """
    engine = DeterministicReconciliationEngine(
        proximity_window_days=req.proximity_window_days,
        sla_delay_threshold_days=req.sla_delay_threshold_days
    )
    result = engine.reconcile_all(
        db=db,
        merchant_id=req.merchant_id,
        clear_existing=req.recalculate_all
    )
    return result


@router.get("/summary", response_model=ReconciliationSummaryResponse)
def get_reconciliation_summary(
    merchant_id: Optional[str] = Query(None, description="Optional merchant filter"),
    db: Session = Depends(get_db)
):
    """
    Retrieves dynamic high-level KPI metrics computed directly from reconciliation results.
    """
    summary = DeterministicReconciliationEngine.compute_summary(db=db, merchant_id=merchant_id)
    return summary


@router.get("/results", response_model=List[ReconciliationItemResponse])
def get_reconciliation_results(
    status: Optional[str] = Query(None, description="Filter by reconciliation status (MATCHED, EXCEPTION, etc.)"),
    classification: Optional[str] = Query(None, description="Filter by classification (FEE_MISMATCH, etc.)"),
    has_discrepancy: Optional[bool] = Query(None, description="Filter by presence of financial discrepancy"),
    search: Optional[str] = Query(None, description="Search by payment ID or reference"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lists paginated reconciliation records with multi-criteria filtering.
    """
    query = db.query(ReconciliationResult).join(Payment, ReconciliationResult.payment_id == Payment.id, isouter=True)

    if status:
        query = query.filter(ReconciliationResult.status == status.upper())
    if classification:
        query = query.filter(ReconciliationResult.classification == classification.upper())
    if has_discrepancy is True:
        query = query.filter(ReconciliationResult.discrepancy_amount != Decimal("0.00"))
    elif has_discrepancy is False:
        query = query.filter(ReconciliationResult.discrepancy_amount == Decimal("0.00"))
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (ReconciliationResult.id.ilike(search_pattern)) |
            (Payment.payment_reference.ilike(search_pattern))
        )

    results = query.order_by(ReconciliationResult.reconciled_at.desc()).offset(offset).limit(limit).all()

    # Enrich with references for clean API presentation
    items: List[ReconciliationItemResponse] = []
    for r in results:
        order = db.query(Order).filter(Order.id == r.order_id).first() if r.order_id else None
        payment = db.query(Payment).filter(Payment.id == r.payment_id).first() if r.payment_id else None
        settlement = db.query(Settlement).filter(Settlement.id == r.settlement_id).first() if r.settlement_id else None
        bank = db.query(BankTransaction).filter(BankTransaction.id == r.bank_transaction_id).first() if r.bank_transaction_id else None

        items.append(ReconciliationItemResponse(
            id=r.id,
            payment_id=r.payment_id,
            order_id=r.order_id,
            settlement_id=r.settlement_id,
            bank_transaction_id=r.bank_transaction_id,
            order_reference=order.order_reference if order else None,
            payment_reference=payment.payment_reference if payment else None,
            settlement_reference=settlement.settlement_reference if settlement else None,
            bank_reference=bank.bank_reference if bank else None,
            utr_number=bank.utr_number if bank else None,
            expected_settlement_amount=r.expected_settlement_amount,
            actual_settlement_amount=r.actual_settlement_amount,
            expected_bank_amount=r.expected_bank_amount,
            actual_bank_amount=r.actual_bank_amount,
            discrepancy_amount=r.discrepancy_amount,
            matching_score=r.matching_score,
            matching_method=r.matching_method,
            status=r.status,
            classification=r.classification,
            operational_warning=r.operational_warning,
            evidence_payload=r.evidence_payload,
            reconciled_at=r.reconciled_at,
        ))

    return items


@router.get("/results/{result_id}", response_model=ReconciliationItemResponse)
def get_reconciliation_result_by_id(
    result_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a single detailed reconciliation result by ID with its complete evidence chain.
    """
    r = db.query(ReconciliationResult).filter(ReconciliationResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Reconciliation result '{result_id}' not found.")

    order = db.query(Order).filter(Order.id == r.order_id).first() if r.order_id else None
    payment = db.query(Payment).filter(Payment.id == r.payment_id).first() if r.payment_id else None
    settlement = db.query(Settlement).filter(Settlement.id == r.settlement_id).first() if r.settlement_id else None
    bank = db.query(BankTransaction).filter(BankTransaction.id == r.bank_transaction_id).first() if r.bank_transaction_id else None

    return ReconciliationItemResponse(
        id=r.id,
        payment_id=r.payment_id,
        order_id=r.order_id,
        settlement_id=r.settlement_id,
        bank_transaction_id=r.bank_transaction_id,
        order_reference=order.order_reference if order else None,
        payment_reference=payment.payment_reference if payment else None,
        settlement_reference=settlement.settlement_reference if settlement else None,
        bank_reference=bank.bank_reference if bank else None,
        utr_number=bank.utr_number if bank else None,
        expected_settlement_amount=r.expected_settlement_amount,
        actual_settlement_amount=r.actual_settlement_amount,
        expected_bank_amount=r.expected_bank_amount,
        actual_bank_amount=r.actual_bank_amount,
        discrepancy_amount=r.discrepancy_amount,
        matching_score=r.matching_score,
        matching_method=r.matching_method,
        status=r.status,
        classification=r.classification,
        operational_warning=r.operational_warning,
        evidence_payload=r.evidence_payload,
        reconciled_at=r.reconciled_at,
    )
