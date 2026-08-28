from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.models.schema import (
    InvestigationResult,
    ReconciliationResult,
    Payment,
    Order,
    Merchant,
    InvestigationStatus,
    AuditLog,
)
from app.ai.investigator import FinancialAIInvestigator
from app.ai.schemas import (
    InvestigationItemResponse,
    InvestigationSummaryResponse,
)

router = APIRouter(prefix="/investigations", tags=["AI Investigation"])


class HumanReviewRequest(BaseModel):
    action: str  # "RESOLVE", "ESCALATE", "ADD_NOTE", "OVERRIDE_EXPLAINED"
    note: str
    reviewer: str = "FINANCE_OPERATOR"

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("/{reconciliation_id}/run", response_model=InvestigationItemResponse)
def run_investigation_on_reconciliation(
    reconciliation_id: str,
    force: bool = Query(False, description="Force re-investigation bypassing cache"),
    db: Session = Depends(get_db)
):
    """
    Triggers evidence-first Groq AI investigation for a specific reconciliation result.
    """
    investigator = FinancialAIInvestigator()
    try:
        inv = investigator.investigate(
            reconciliation_id=reconciliation_id,
            db=db,
            force_reinvestigate=force
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")

    rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == inv.reconciliation_id).first()
    payment = db.query(Payment).filter(Payment.id == rec.payment_id).first() if rec else None
    order = db.query(Order).filter(Order.id == rec.order_id).first() if (rec and rec.order_id) else None
    merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first() if order else None

    return InvestigationItemResponse(
        id=inv.id,
        reconciliation_id=inv.reconciliation_id,
        payment_id=rec.payment_id if rec else "unknown",
        order_reference=order.order_reference if order else None,
        payment_reference=payment.payment_reference if payment else None,
        merchant_id=merchant.id if merchant else None,
        merchant_name=merchant.name if merchant else None,
        payment_amount=payment.amount if payment else Decimal("0.00"),
        discrepancy_amount=rec.discrepancy_amount if rec else Decimal("0.00"),
        reconciliation_status=rec.status if rec else "MATCHED",
        reconciliation_classification=rec.classification if rec else "NONE",
        investigation_status=inv.investigation_status,
        summary=inv.summary,
        facts=inv.facts or [],
        explanation=inv.explanation,
        evidence_references=inv.evidence_references or [],
        missing_evidence=inv.missing_evidence or [],
        ai_confidence=float(inv.ai_confidence),
        system_confidence=float(inv.system_confidence),
        confidence_tier=inv.confidence_tier,
        recommended_action=inv.recommended_action,
        human_override=inv.human_override,
        reviewer_note=inv.reviewer_note,
        cached=inv.cached,
        latency_ms=float(inv.latency_ms),
        model_name=inv.model_name,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
    )


@router.post("/{investigation_id}/review", response_model=InvestigationItemResponse)
def submit_human_review_action(
    investigation_id: str,
    req: HumanReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Records a human operator review decision and creates an immutable audit trail entry.
    """
    inv = db.query(InvestigationResult).filter(InvestigationResult.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Investigation '{investigation_id}' not found.")

    prev_status = inv.investigation_status
    prev_note = inv.reviewer_note

    inv.human_override = True
    inv.reviewer_note = f"{req.reviewer}: {req.note}" if not inv.reviewer_note else f"{inv.reviewer_note} | {req.reviewer}: {req.note}"
    
    if req.action == "RESOLVE" or req.action == "OVERRIDE_EXPLAINED":
        inv.investigation_status = InvestigationStatus.EXPLAINED
        inv.recommended_action = "RESOLVED_BY_OPERATOR"
    elif req.action == "ESCALATE":
        inv.investigation_status = InvestigationStatus.HUMAN_REVIEW_REQUIRED
        inv.recommended_action = "ESCALATED_TO_TREASURY"
    elif req.action == "ADD_NOTE":
        pass  # keep status, append note

    inv.updated_at = datetime.utcnow()

    # Record Audit Log
    audit = AuditLog(
        id=f"aud_{int(datetime.utcnow().timestamp()*1000)}",
        entity_type="INVESTIGATION_OVERRIDE",
        entity_id=inv.id,
        action=f"HUMAN_REVIEW_{req.action}",
        actor=req.reviewer,
        previous_state={"status": str(prev_status), "reviewer_note": prev_note},
        new_state={"status": str(inv.investigation_status), "reviewer_note": inv.reviewer_note},
        notes=req.note,
    )
    db.add(audit)
    db.commit()

    rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == inv.reconciliation_id).first()
    payment = db.query(Payment).filter(Payment.id == rec.payment_id).first() if rec else None
    order = db.query(Order).filter(Order.id == rec.order_id).first() if (rec and rec.order_id) else None
    merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first() if order else None

    return InvestigationItemResponse(
        id=inv.id,
        reconciliation_id=inv.reconciliation_id,
        payment_id=rec.payment_id if rec else "unknown",
        order_reference=order.order_reference if order else None,
        payment_reference=payment.payment_reference if payment else None,
        merchant_id=merchant.id if merchant else None,
        merchant_name=merchant.name if merchant else None,
        payment_amount=payment.amount if payment else Decimal("0.00"),
        discrepancy_amount=rec.discrepancy_amount if rec else Decimal("0.00"),
        reconciliation_status=rec.status if rec else "MATCHED",
        reconciliation_classification=rec.classification if rec else "NONE",
        investigation_status=inv.investigation_status,
        summary=inv.summary,
        facts=inv.facts or [],
        explanation=inv.explanation,
        evidence_references=inv.evidence_references or [],
        missing_evidence=inv.missing_evidence or [],
        ai_confidence=float(inv.ai_confidence),
        system_confidence=float(inv.system_confidence),
        confidence_tier=inv.confidence_tier,
        recommended_action=inv.recommended_action,
        human_override=inv.human_override,
        reviewer_note=inv.reviewer_note,
        cached=inv.cached,
        latency_ms=float(inv.latency_ms),
        model_name=inv.model_name,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
    )


@router.get("/{investigation_id}/audit-logs", response_model=List[AuditLogResponse])
def get_investigation_audit_logs(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns the complete chronological audit timeline for an investigation.
    """
    logs = db.query(AuditLog).filter(
        AuditLog.entity_id.in_([investigation_id, investigation_id.replace("inv_", "rec_")])
    ).order_by(AuditLog.created_at.asc()).all()

    return [
        AuditLogResponse(
            id=l.id,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            action=l.action,
            actor=l.actor,
            previous_state=l.previous_state,
            new_state=l.new_state,
            notes=l.notes,
            created_at=l.created_at,
        )
        for l in logs
    ]


@router.get("/summary", response_model=InvestigationSummaryResponse)
def get_investigation_summary(
    db: Session = Depends(get_db)
):
    """
    Retrieves summary statistics for completed AI investigations.
    """
    return FinancialAIInvestigator.compute_summary(db=db)


@router.get("", response_model=List[InvestigationItemResponse])
def list_investigations(
    status: Optional[str] = Query(None, description="Filter by investigation status"),
    confidence_tier: Optional[str] = Query(None, description="Filter by confidence tier (HIGH, MEDIUM, LOW)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lists paginated investigation results with multi-criteria filtering.
    """
    query = db.query(InvestigationResult).join(
        ReconciliationResult, InvestigationResult.reconciliation_id == ReconciliationResult.id
    )

    if status:
        query = query.filter(InvestigationResult.investigation_status == status.upper())
    if confidence_tier:
        query = query.filter(InvestigationResult.confidence_tier == confidence_tier.upper())

    results = query.order_by(InvestigationResult.created_at.desc()).offset(offset).limit(limit).all()

    items: List[InvestigationItemResponse] = []
    for inv in results:
        rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == inv.reconciliation_id).first()
        payment = db.query(Payment).filter(Payment.id == rec.payment_id).first() if rec else None
        order = db.query(Order).filter(Order.id == rec.order_id).first() if (rec and rec.order_id) else None
        merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first() if order else None

        items.append(InvestigationItemResponse(
            id=inv.id,
            reconciliation_id=inv.reconciliation_id,
            payment_id=rec.payment_id if rec else "unknown",
            order_reference=order.order_reference if order else None,
            payment_reference=payment.payment_reference if payment else None,
            merchant_id=merchant.id if merchant else None,
            merchant_name=merchant.name if merchant else None,
            payment_amount=payment.amount if payment else Decimal("0.00"),
            discrepancy_amount=rec.discrepancy_amount if rec else Decimal("0.00"),
            reconciliation_status=rec.status if rec else "MATCHED",
            reconciliation_classification=rec.classification if rec else "NONE",
            investigation_status=inv.investigation_status,
            summary=inv.summary,
            facts=inv.facts or [],
            explanation=inv.explanation,
            evidence_references=inv.evidence_references or [],
            missing_evidence=inv.missing_evidence or [],
            ai_confidence=float(inv.ai_confidence),
            system_confidence=float(inv.system_confidence),
            confidence_tier=inv.confidence_tier,
            recommended_action=inv.recommended_action,
            human_override=inv.human_override,
            reviewer_note=inv.reviewer_note,
            cached=inv.cached,
            latency_ms=float(inv.latency_ms),
            model_name=inv.model_name,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
        ))

    return items


@router.get("/{investigation_id}", response_model=InvestigationItemResponse)
def get_investigation_by_id(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a single detailed investigation by ID.
    """
    inv = db.query(InvestigationResult).filter(
        (InvestigationResult.id == investigation_id) |
        (InvestigationResult.reconciliation_id == investigation_id)
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Investigation '{investigation_id}' not found.")

    rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == inv.reconciliation_id).first()
    payment = db.query(Payment).filter(Payment.id == rec.payment_id).first() if rec else None
    order = db.query(Order).filter(Order.id == rec.order_id).first() if (rec and rec.order_id) else None
    merchant = db.query(Merchant).filter(Merchant.id == order.merchant_id).first() if order else None

    return InvestigationItemResponse(
        id=inv.id,
        reconciliation_id=inv.reconciliation_id,
        payment_id=rec.payment_id if rec else "unknown",
        order_reference=order.order_reference if order else None,
        payment_reference=payment.payment_reference if payment else None,
        merchant_id=merchant.id if merchant else None,
        merchant_name=merchant.name if merchant else None,
        payment_amount=payment.amount if payment else Decimal("0.00"),
        discrepancy_amount=rec.discrepancy_amount if rec else Decimal("0.00"),
        reconciliation_status=rec.status if rec else "MATCHED",
        reconciliation_classification=rec.classification if rec else "NONE",
        investigation_status=inv.investigation_status,
        summary=inv.summary,
        facts=inv.facts or [],
        explanation=inv.explanation,
        evidence_references=inv.evidence_references or [],
        missing_evidence=inv.missing_evidence or [],
        ai_confidence=float(inv.ai_confidence),
        system_confidence=float(inv.system_confidence),
        confidence_tier=inv.confidence_tier,
        recommended_action=inv.recommended_action,
        human_override=inv.human_override,
        reviewer_note=inv.reviewer_note,
        cached=inv.cached,
        latency_ms=float(inv.latency_ms),
        model_name=inv.model_name,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
    )
