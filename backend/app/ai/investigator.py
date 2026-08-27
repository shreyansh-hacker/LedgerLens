import time
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.schema import (
    ReconciliationResult,
    InvestigationResult,
    InvestigationStatus,
    AuditLog,
)
from app.ai.evidence import EvidenceAssembler
from app.ai.provider import AIProvider, GroqProvider
from app.ai.confidence import SystemConfidenceEvaluator
from app.ai.schemas import StructuredAIInvestigation, FactualClaim, InvestigationItemResponse, InvestigationSummaryResponse


class FinancialAIInvestigator:
    """
    Evidence-First AI Financial Investigator.
    Translates raw ledger discrepancies into verifiable, grounded explanations.
    Enforces canonical SHA-256 evidence caching, multi-factor confidence scoring,
    and graceful deterministic fallbacks.
    """

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or GroqProvider()

    def investigate(
        self,
        reconciliation_id: str,
        db: Session,
        force_reinvestigate: bool = False
    ) -> InvestigationResult:
        rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == reconciliation_id).first()
        if not rec:
            raise ValueError(f"ReconciliationResult '{reconciliation_id}' not found.")

        # 1. Assemble structured evidence packet & compute canonical hash
        evidence_data = EvidenceAssembler.assemble_evidence(reconciliation_result=rec, db=db)
        evidence_packet = evidence_data["evidence"]
        evidence_hash = evidence_data["evidence_hash"]

        # 2. Check Investigation Cache
        existing = db.query(InvestigationResult).filter(
            InvestigationResult.reconciliation_id == rec.id,
            InvestigationResult.evidence_hash == evidence_hash
        ).first()

        if existing and not force_reinvestigate and not existing.human_override:
            existing.cached = True
            db.commit()
            return existing

        # 3. Call AI Provider (Groq)
        ai_output, raw_resp, latency_ms = self.provider.investigate(evidence_packet)

        # 4. Fallback if AI provider is unavailable
        if not ai_output:
            ai_output = self._create_deterministic_fallback(rec, evidence_packet)

        # 5. Evaluate System Confidence
        confidence_result = SystemConfidenceEvaluator.evaluate(
            evidence=evidence_packet,
            ai_output=ai_output
        )

        inv_id = f"inv_{rec.id.replace('rec_', '')}"
        investigation = db.query(InvestigationResult).filter(InvestigationResult.id == inv_id).first()
        if not investigation:
            investigation = InvestigationResult(id=inv_id, reconciliation_id=rec.id)

        facts_json = [f.model_dump() if hasattr(f, "model_dump") else f for f in ai_output.facts]

        investigation.evidence_hash = evidence_hash
        investigation.investigation_status = ai_output.status
        investigation.summary = ai_output.summary
        investigation.facts = facts_json
        investigation.explanation = ai_output.explanation
        investigation.evidence_references = ai_output.evidence_references
        investigation.missing_evidence = ai_output.missing_evidence
        investigation.ai_confidence = Decimal(f"{ai_output.confidence:.2f}")
        investigation.system_confidence = Decimal(f"{confidence_result['system_confidence']:.2f}")
        investigation.confidence_tier = confidence_result["confidence_tier"]
        investigation.recommended_action = ai_output.recommended_action
        investigation.cached = False
        investigation.latency_ms = Decimal(f"{latency_ms:.2f}")
        investigation.model_name = getattr(self.provider, "model_name", "llama-3.3-70b-versatile")
        investigation.updated_at = datetime.utcnow()

        db.add(investigation)

        # 6. Record Audit Log
        audit = AuditLog(
            id=f"aud_{int(time.time()*1000)}",
            entity_type="INVESTIGATION",
            entity_id=investigation.id,
            action="RUN_INVESTIGATION",
            actor="AI_INVESTIGATOR",
            previous_state=None,
            new_state={
                "status": ai_output.status,
                "system_confidence": confidence_result["system_confidence"],
                "evidence_hash": evidence_hash,
            },
            notes=f"Investigated reconciliation {rec.id} using {investigation.model_name} in {latency_ms:.1f}ms",
        )
        db.add(audit)
        db.commit()

        return investigation

    def _create_deterministic_fallback(
        self,
        rec: ReconciliationResult,
        evidence: Dict[str, Any]
    ) -> StructuredAIInvestigation:
        """
        Graceful fallback when AI provider is unavailable.
        Maintains product uptime and zero-panic error handling.
        """
        disc = rec.discrepancy_amount
        classification = rec.classification

        if rec.status == "MATCHED":
            return StructuredAIInvestigation(
                status=InvestigationStatus.EXPLAINED,
                summary="Transaction fully reconciles across payment, fee schedule, and bank credit.",
                facts=[
                    FactualClaim(statement=f"Payment amount: ₹{rec.expected_settlement_amount}", evidence_ids=[rec.payment_id]),
                ],
                explanation="All recorded amounts match expected settlement figures without discrepancy.",
                evidence_references=[rec.payment_id],
                missing_evidence=[],
                confidence=95.0,
                recommended_action="NO_ACTION"
            )

        if classification in ["UNEXPLAINED", "UNEXPLAINED_EXCEPTION"]:
            return StructuredAIInvestigation(
                status=InvestigationStatus.HUMAN_REVIEW_REQUIRED,
                summary=f"Unexplained financial discrepancy of ₹{abs(disc)} detected.",
                facts=[
                    FactualClaim(statement=f"Unaccounted financial variance of ₹{abs(disc)}", evidence_ids=[rec.id]),
                ],
                explanation="Known records contain no matching fee, tax, or refund justifying this discrepancy.",
                evidence_references=[rec.payment_id],
                missing_evidence=["Adjustment note", "Bank statement charge slip"],
                confidence=40.0,
                recommended_action="HUMAN_REVIEW"
            )

        return StructuredAIInvestigation(
            status=InvestigationStatus.HUMAN_REVIEW_REQUIRED,
            summary=f"Reconciliation exception flagged ({classification}) for ₹{abs(disc)}.",
            facts=[
                FactualClaim(statement=f"Classification: {classification}", evidence_ids=[rec.id]),
            ],
            explanation="AI investigation service is temporarily unreachable. Deterministic evidence trail is available for manual review.",
            evidence_references=[rec.payment_id],
            missing_evidence=[],
            confidence=60.0,
            recommended_action="HUMAN_REVIEW"
        )

    @classmethod
    def compute_summary(cls, db: Session) -> InvestigationSummaryResponse:
        results: List[InvestigationResult] = db.query(InvestigationResult).all()
        total = len(results)
        if total == 0:
            return InvestigationSummaryResponse()

        explained = sum(1 for r in results if r.investigation_status == InvestigationStatus.EXPLAINED)
        part_explained = sum(1 for r in results if r.investigation_status == InvestigationStatus.PARTIALLY_EXPLAINED)
        human_review = sum(1 for r in results if r.investigation_status == InvestigationStatus.HUMAN_REVIEW_REQUIRED)
        conflicts = sum(1 for r in results if r.investigation_status == InvestigationStatus.CONFLICTING_EVIDENCE)
        
        avg_conf = sum((float(r.system_confidence) for r in results), 0.0) / total
        cached_count = sum(1 for r in results if r.cached)

        return InvestigationSummaryResponse(
            total_investigations=total,
            explained_count=explained,
            partially_explained_count=part_explained,
            human_review_count=human_review,
            conflicting_evidence_count=conflicts,
            avg_system_confidence=round(avg_conf, 2),
            cached_rate_percentage=round((cached_count / total) * 100.0, 2),
        )
