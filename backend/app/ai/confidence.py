from typing import Dict, Any, List
from app.ai.schemas import StructuredAIInvestigation


class SystemConfidenceEvaluator:
    """
    Computes system-level composite confidence scores combining:
    - Deterministic calculation agreement
    - Evidence completeness
    - Matching confidence
    - AI evidence grounding
    - Anomaly risk penalty
    """

    @classmethod
    def evaluate(
        cls,
        evidence: Dict[str, Any],
        ai_output: StructuredAIInvestigation,
    ) -> Dict[str, Any]:
        rec_sum = evidence.get("reconciliation_summary", {})
        disc_val = float(rec_sum.get("discrepancy_amount", "0.00"))
        matching_score = float(rec_sum.get("matching_score", 100.0))
        anom_ctx = evidence.get("anomaly_context", {})
        anom_sev = anom_ctx.get("severity", "LOW")

        # 1. Evidence Completeness (0 - 100)
        completeness = 100.0
        if not evidence.get("settlement"):
            completeness -= 35.0
        if not evidence.get("bank_transaction"):
            completeness -= 35.0
        if not evidence.get("recorded_fees"):
            completeness -= 10.0
        completeness = max(10.0, completeness)

        # 2. Calculation Agreement (0 - 100)
        # If no discrepancy or cleanly explained by records -> 100; if unexplained gap -> penalized
        if disc_val == 0.0:
            calc_agreement = 100.0
        elif ai_output.status == "EXPLAINED":
            calc_agreement = 95.0
        elif ai_output.status == "PARTIALLY_EXPLAINED":
            calc_agreement = 65.0
        else:
            calc_agreement = 30.0  # Unexplained discrepancy

        # 3. AI Evidence Grounding (0 - 100)
        valid_ids = set()
        payment_dict = evidence.get("payment") or {}
        if payment_dict.get("id"):
            valid_ids.add(payment_dict["id"])

        order_dict = evidence.get("order") or {}
        if order_dict.get("id"):
            valid_ids.add(order_dict["id"])

        for f in (evidence.get("recorded_fees") or []):
            if f.get("id"):
                valid_ids.add(f["id"])

        for t in (evidence.get("recorded_taxes") or []):
            if t.get("id"):
                valid_ids.add(t["id"])

        for r in (evidence.get("recorded_refunds") or []):
            if r.get("id"):
                valid_ids.add(r["id"])

        settlement_dict = evidence.get("settlement") or {}
        if settlement_dict.get("id"):
            valid_ids.add(settlement_dict["id"])

        bank_dict = evidence.get("bank_transaction") or {}
        if bank_dict.get("id"):
            valid_ids.add(bank_dict["id"])

        cited_ids = set(ai_output.evidence_references)
        for fact in ai_output.facts:
            cited_ids.update(fact.evidence_ids)

        if not cited_ids:
            grounding_score = 70.0
        else:
            valid_cited = sum(1 for cid in cited_ids if cid in valid_ids or cid.startswith(("pay_", "ord_", "fee_", "tax_", "set_", "bnk_", "PAY_", "ORD_", "SET_", "BNK_")))
            grounding_score = (valid_cited / len(cited_ids)) * 100.0

        # 4. Anomaly Penalty
        anomaly_penalty = 0.0
        if anom_sev == "HIGH":
            anomaly_penalty = 10.0
        elif anom_sev == "MEDIUM":
            anomaly_penalty = 4.0

        # Composite Score Calculation
        composite = (
            (calc_agreement * 0.35) +
            (completeness * 0.25) +
            (matching_score * 0.20) +
            (grounding_score * 0.20) -
            anomaly_penalty
        )
        composite = round(max(5.0, min(99.0, composite)), 2)

        if composite >= 88.0:
            tier = "HIGH"
        elif composite >= 60.0:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        return {
            "system_confidence": composite,
            "confidence_tier": tier,
            "components": {
                "calculation_agreement": calc_agreement,
                "evidence_completeness": completeness,
                "matching_confidence": matching_score,
                "grounding_score": grounding_score,
                "anomaly_penalty": anomaly_penalty,
            }
        }
