import time
import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.models.schema import (
    Payment,
    Order,
    Fee,
    Tax,
    Refund,
    Settlement,
    BankTransaction,
    ReconciliationResult,
    ReconciliationStatus,
    AnomalyResult,
    InvestigationResult,
    AuditLog,
)
from app.reconciliation.calculator import FinancialCalculator, quantize_money
from app.reconciliation.matching import MultiPassMatcher
from app.reconciliation.classifier import ExceptionClassifier
from app.reconciliation.schemas import (
    ReconciliationSummaryResponse,
    ReconciliationRunResult,
    ReconciliationEvidencePayload,
)


class DeterministicReconciliationEngine:
    """
    Core Deterministic Reconciliation Engine.
    Executes multi-pass matching, exact precision financial arithmetic,
    missing/duplicate record detection, and rule-based exception classification.
    """

    def __init__(
        self,
        proximity_window_days: int = 5,
        sla_delay_threshold_days: int = 7,
    ):
        self.proximity_window_days = proximity_window_days
        self.sla_delay_threshold_days = sla_delay_threshold_days
        self.matcher = MultiPassMatcher(proximity_window_days=proximity_window_days)

    def reconcile_all(
        self,
        db: Session,
        merchant_id: Optional[str] = None,
        clear_existing: bool = True
    ) -> ReconciliationRunResult:
        """
        Executes full reconciliation across all payments in the database.
        """
        start_time = time.perf_counter()

        # 1. Fetch observable financial entities
        payment_query = db.query(Payment)
        if merchant_id:
            payment_query = payment_query.join(Order).filter(Order.merchant_id == merchant_id)
        payments: List[Payment] = payment_query.all()

        orders_by_id = {o.id: o for o in db.query(Order).all()}
        fees_by_payment_id: Dict[str, List[Fee]] = {}
        for f in db.query(Fee).all():
            fees_by_payment_id.setdefault(f.payment_id, []).append(f)

        taxes_by_payment_id: Dict[str, List[Tax]] = {}
        for t in db.query(Tax).all():
            taxes_by_payment_id.setdefault(t.payment_id, []).append(t)

        refunds_by_payment_id: Dict[str, List[Refund]] = {}
        for r in db.query(Refund).all():
            refunds_by_payment_id.setdefault(r.payment_id, []).append(r)

        all_settlements = db.query(Settlement).all()
        settlements_by_payment_id: Dict[str, List[Settlement]] = {}
        settlements_by_ref: Dict[str, Settlement] = {}
        unmatched_settlements_dict: Dict[str, Settlement] = {}

        for s in all_settlements:
            unmatched_settlements_dict[s.id] = s
            if s.payment_id and not s.payment_id.startswith("pay_unknown"):
                settlements_by_payment_id.setdefault(s.payment_id, []).append(s)
            if s.settlement_reference:
                clean = s.settlement_reference.replace("SET_", "").replace("PAY_", "")
                settlements_by_ref[clean] = s

        all_bank_txns = db.query(BankTransaction).all()
        bank_by_settlement_id: Dict[str, BankTransaction] = {
            b.settlement_id: b for b in all_bank_txns if b.settlement_id
        }
        bank_by_reference: Dict[str, BankTransaction] = {}
        for b in all_bank_txns:
            if b.bank_reference:
                clean_b = b.bank_reference.replace("TXN_", "").replace("SET_", "")
                bank_by_reference[clean_b] = b

        # Clear existing reconciliation results and dependent records in reverse-dependency order
        if clear_existing:
            for model in [AuditLog, InvestigationResult, AnomalyResult, ReconciliationResult]:
                db.query(model).delete(synchronize_session=False)
            db.commit()

        results_to_insert: List[Dict[str, Any]] = []

        for pay in payments:
            order = orders_by_id.get(pay.order_id)
            fees = fees_by_payment_id.get(pay.id, [])
            taxes = taxes_by_payment_id.get(pay.id, [])
            refunds = refunds_by_payment_id.get(pay.id, [])

            # Match settlement with indexed lookup
            unmatched_list = list(unmatched_settlements_dict.values())
            (
                settlement,
                duplicate_settlements,
                matching_method,
                matching_score,
                match_signals,
                competing_candidates,
            ) = self.matcher.match_payment_to_settlements(
                payment=pay,
                unmatched_settlements=unmatched_list,
                all_settlements_by_payment_id=settlements_by_payment_id,
                settlements_by_ref=settlements_by_ref,
            )

            if settlement:
                unmatched_settlements_dict.pop(settlement.id, None)
            for d in duplicate_settlements:
                unmatched_settlements_dict.pop(d.id, None)

            # Match bank transaction
            (
                bank_txn,
                bank_match_method,
                bank_match_score,
                bank_signals,
            ) = self.matcher.match_settlement_to_bank(
                settlement=settlement,
                all_bank_transactions=all_bank_txns,
                bank_by_settlement_id=bank_by_settlement_id,
                bank_by_reference=bank_by_reference,
            )

            # Deterministic Calculations
            calc_summary = FinancialCalculator.calculate_expected_settlement(
                payment_amount=pay.amount,
                fees=fees,
                taxes=taxes,
                refunds=refunds
            )

            disc_summary = FinancialCalculator.calculate_discrepancy(
                expected_settlement=calc_summary["expected_net_settlement"],
                actual_settlement_net=settlement.net_amount if settlement else None,
                actual_bank_credit=bank_txn.credit_amount if bank_txn else None
            )

            merged_calc = {**calc_summary, **disc_summary}

            # Classify condition
            (
                status,
                classification,
                operational_warning,
                classified_signals,
            ) = ExceptionClassifier.classify(
                payment=pay,
                order=order,
                fees=fees,
                taxes=taxes,
                refunds=refunds,
                settlement=settlement,
                bank=bank_txn,
                duplicate_settlements=duplicate_settlements,
                calc_result=merged_calc,
                matching_method=matching_method,
                matching_score=matching_score,
                signals=match_signals + bank_signals,
                sla_delay_threshold_days=self.sla_delay_threshold_days
            )

            # Build structured machine-readable evidence
            evidence = ReconciliationEvidencePayload(
                matched_by=[matching_method, bank_match_method] if settlement else [matching_method],
                matching_confidence=float(matching_score),
                matching_method=matching_method,
                calculation={
                    "payment_gross": str(merged_calc["payment_gross"]),
                    "total_fees": str(merged_calc["total_fees"]),
                    "total_taxes": str(merged_calc["total_taxes"]),
                    "total_refunds": str(merged_calc["total_refunds"]),
                    "expected_net_settlement": str(merged_calc["expected_net_settlement"]),
                    "actual_settlement_net": str(settlement.net_amount) if settlement else None,
                    "actual_bank_credit": str(bank_txn.credit_amount) if bank_txn else None,
                    "discrepancy_amount": str(merged_calc["discrepancy_amount"]),
                },
                evidence_references={
                    "order_reference": order.order_reference if order else None,
                    "payment_reference": pay.payment_reference,
                    "settlement_reference": settlement.settlement_reference if settlement else None,
                    "bank_reference": bank_txn.bank_reference if bank_txn else None,
                    "utr_number": bank_txn.utr_number if bank_txn else None,
                },
                signals=classified_signals,
                competing_candidates=competing_candidates,
            )

            results_to_insert.append({
                "id": f"rec_{pay.id.replace('pay_', '')}",
                "payment_id": pay.id,
                "order_id": order.id if order else None,
                "settlement_id": settlement.id if settlement else None,
                "bank_transaction_id": bank_txn.id if bank_txn else None,
                "expected_settlement_amount": calc_summary["expected_net_settlement"],
                "actual_settlement_amount": settlement.net_amount if settlement else None,
                "expected_bank_amount": calc_summary["expected_bank_amount"],
                "actual_bank_amount": bank_txn.credit_amount if bank_txn else None,
                "discrepancy_amount": disc_summary["discrepancy_amount"],
                "matching_score": Decimal(str(matching_score)),
                "matching_method": matching_method,
                "status": status,
                "classification": classification,
                "operational_warning": operational_warning,
                "evidence_payload": evidence.model_dump(),
                "reconciled_at": datetime.utcnow(),
            })

        for i in range(0, len(results_to_insert), 500):
            chunk = results_to_insert[i:i + 500]
            if chunk:
                db.execute(insert(ReconciliationResult).values(chunk))
        db.commit()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        summary = self.compute_summary(db, merchant_id=merchant_id)

        return ReconciliationRunResult(
            status="success",
            processed_count=len(results_to_insert),
            duration_ms=round(elapsed_ms, 2),
            summary=summary,
        )

    @classmethod
    def compute_summary(cls, db: Session, merchant_id: Optional[str] = None) -> ReconciliationSummaryResponse:
        """
        Computes aggregated summary KPIs dynamically from the database.
        """
        query = db.query(ReconciliationResult)
        if merchant_id:
            query = query.join(Payment).join(Order).filter(Order.merchant_id == merchant_id)
        
        all_results: List[ReconciliationResult] = query.all()
        total_records = len(all_results)
        
        if total_records == 0:
            return ReconciliationSummaryResponse()

        matched_count = sum(1 for r in all_results if r.status == ReconciliationStatus.MATCHED)
        exception_count = sum(1 for r in all_results if r.status == ReconciliationStatus.EXCEPTION)
        missing_bank_count = sum(1 for r in all_results if r.status == ReconciliationStatus.MISSING_BANK_TRANSACTION)
        missing_settlement_count = sum(1 for r in all_results if r.status == ReconciliationStatus.MISSING_SETTLEMENT)
        duplicate_count = sum(1 for r in all_results if r.status == ReconciliationStatus.DUPLICATE)
        review_count = sum(1 for r in all_results if r.status == ReconciliationStatus.REVIEW)

        match_rate = (matched_count / total_records) * 100.0

        total_expected = sum((r.expected_settlement_amount for r in all_results), Decimal("0.00"))
        total_actual = sum((r.actual_bank_amount for r in all_results if r.actual_bank_amount), Decimal("0.00"))
        total_discrepancy = sum((abs(r.discrepancy_amount) for r in all_results), Decimal("0.00"))

        # Explained by deterministic rules vs unexplainable
        explained_amount = sum(
            (abs(r.discrepancy_amount) for r in all_results if r.classification not in ["UNEXPLAINED", "UNEXPLAINED_EXCEPTION"]),
            Decimal("0.00")
        )
        unresolved_amount = sum(
            (abs(r.discrepancy_amount) for r in all_results if r.classification in ["UNEXPLAINED", "UNEXPLAINED_EXCEPTION"]),
            Decimal("0.00")
        )

        classifications: Dict[str, int] = {}
        operational_warnings = 0
        for r in all_results:
            classifications[r.classification] = classifications.get(r.classification, 0) + 1
            if r.operational_warning:
                operational_warnings += 1

        return ReconciliationSummaryResponse(
            total_records=total_records,
            matched_count=matched_count,
            exception_count=exception_count,
            missing_bank_count=missing_bank_count,
            missing_settlement_count=missing_settlement_count,
            duplicate_count=duplicate_count,
            review_count=review_count,
            match_rate_percentage=round(match_rate, 2),
            total_expected_amount=quantize_money(total_expected),
            total_actual_amount=quantize_money(total_actual),
            total_discrepancy_amount=quantize_money(total_discrepancy),
            total_explained_by_rules_amount=quantize_money(explained_amount),
            total_unresolved_amount=quantize_money(unresolved_amount),
            classification_breakdown=classifications,
            operational_warnings_count=operational_warnings,
        )
