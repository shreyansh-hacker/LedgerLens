import json
import hashlib
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.schema import (
    ReconciliationResult,
    Payment,
    Order,
    Fee,
    Tax,
    Refund,
    Settlement,
    BankTransaction,
    AnomalyResult,
)


class EvidenceAssembler:
    """
    Assembles structured, sanitized financial evidence packets for the AI Investigator.
    Produces canonical SHA-256 evidence hashes for zero-waste caching.
    """

    @classmethod
    def assemble_evidence(
        cls,
        reconciliation_result: ReconciliationResult,
        db: Session
    ) -> Dict[str, Any]:
        rec = reconciliation_result

        # Fetch observable financial relations
        payment = db.query(Payment).filter(Payment.id == rec.payment_id).first()
        order = db.query(Order).filter(Order.id == rec.order_id).first() if rec.order_id else None
        fees = db.query(Fee).filter(Fee.payment_id == rec.payment_id).all()
        taxes = db.query(Tax).filter(Tax.payment_id == rec.payment_id).all()
        refunds = db.query(Refund).filter(Refund.payment_id == rec.payment_id).all()
        settlement = db.query(Settlement).filter(Settlement.id == rec.settlement_id).first() if rec.settlement_id else None
        bank = db.query(BankTransaction).filter(BankTransaction.id == rec.bank_transaction_id).first() if rec.bank_transaction_id else None
        anomaly = db.query(AnomalyResult).filter(AnomalyResult.reconciliation_id == rec.id).first()

        evidence_packet = {
            "reconciliation_summary": {
                "reconciliation_id": rec.id,
                "status": rec.status.value if hasattr(rec.status, "value") else str(rec.status),
                "classification": rec.classification,
                "discrepancy_amount": str(rec.discrepancy_amount),
                "expected_settlement_amount": str(rec.expected_settlement_amount),
                "actual_settlement_amount": str(rec.actual_settlement_amount) if rec.actual_settlement_amount is not None else None,
                "expected_bank_amount": str(rec.expected_bank_amount),
                "actual_bank_amount": str(rec.actual_bank_amount) if rec.actual_bank_amount is not None else None,
                "matching_method": rec.matching_method,
                "matching_score": float(rec.matching_score),
                "operational_warning": rec.operational_warning,
            },
            "payment": {
                "id": payment.id if payment else "UNKNOWN",
                "reference": payment.payment_reference if payment else None,
                "amount": str(payment.amount) if payment else "0.00",
                "currency": payment.currency if payment else "INR",
                "gateway_name": payment.gateway_name if payment else "Razorpay",
                "captured_at": payment.captured_at.isoformat() if payment and payment.captured_at else None,
            },
            "order": {
                "id": order.id if order else None,
                "reference": order.order_reference if order else None,
                "amount": str(order.total_amount) if order else None,
                "merchant_id": order.merchant_id if order else None,
            } if order else None,
            "recorded_fees": [
                {
                    "id": f.id,
                    "type": f.fee_type,
                    "rate_percentage": str(f.rate_percentage) if f.rate_percentage is not None else None,
                    "amount": str(f.amount),
                }
                for f in fees
            ],
            "recorded_taxes": [
                {
                    "id": t.id,
                    "type": t.tax_type,
                    "rate_percentage": str(t.rate_percentage) if t.rate_percentage is not None else None,
                    "amount": str(t.amount),
                }
                for t in taxes
            ],
            "recorded_refunds": [
                {
                    "id": r.id,
                    "reference": r.refund_reference,
                    "amount": str(r.amount),
                    "reason": r.reason,
                }
                for r in refunds
            ],
            "settlement": {
                "id": settlement.id,
                "reference": settlement.settlement_reference,
                "gross_amount": str(settlement.gross_amount),
                "fee_deducted": str(settlement.fee_amount),
                "tax_deducted": str(settlement.tax_amount),
                "net_amount": str(settlement.net_amount),
                "settled_at": settlement.settled_at.isoformat() if settlement.settled_at else None,
            } if settlement else None,
            "bank_transaction": {
                "id": bank.id,
                "reference": bank.bank_reference,
                "utr_number": bank.utr_number,
                "credit_amount": str(bank.credit_amount),
                "transaction_date": bank.transaction_date.isoformat() if bank.transaction_date else None,
            } if bank else None,
            "anomaly_context": {
                "normalized_score": float(anomaly.normalized_score) if anomaly else 0.0,
                "severity": anomaly.severity.value if anomaly and hasattr(anomaly.severity, "value") else (str(anomaly.severity) if anomaly else "LOW"),
                "is_anomaly": anomaly.is_anomaly if anomaly else False,
                "contributing_signals": anomaly.explanation_signals if anomaly else [],
            },
        }

        # Calculate Canonical Evidence Hash (SHA-256)
        canonical_json = json.dumps(evidence_packet, sort_keys=True, separators=(",", ":"))
        evidence_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

        return {
            "evidence": evidence_packet,
            "evidence_hash": evidence_hash,
            "canonical_json": canonical_json,
        }
