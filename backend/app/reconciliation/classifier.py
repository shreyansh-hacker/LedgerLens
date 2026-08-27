from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from app.models.schema import (
    Payment,
    Order,
    Fee,
    Tax,
    Refund,
    Settlement,
    BankTransaction,
    ReconciliationStatus,
)
from app.reconciliation.calculator import quantize_money


class ExceptionClassifier:
    """
    Deterministic Rule-Based Exception Classifier.
    Infers the true observable financial condition strictly from database records.
    Never inspects or imports hidden ground-truth metadata.
    """

    GST_RATE = Decimal("0.18")

    @classmethod
    def classify(
        cls,
        payment: Payment,
        order: Optional[Order],
        fees: List[Fee],
        taxes: List[Tax],
        refunds: List[Refund],
        settlement: Optional[Settlement],
        bank: Optional[BankTransaction],
        duplicate_settlements: List[Settlement],
        calc_result: Dict[str, Any],
        matching_method: str,
        matching_score: float,
        signals: List[str],
        sla_delay_threshold_days: int = 7
    ) -> Tuple[ReconciliationStatus, str, Optional[str], List[str]]:
        """
        Returns:
            (reconciliation_status, classification_name, operational_warning, detected_signals)
        """
        all_signals = list(signals)
        operational_warning = None

        expected_settlement = calc_result["expected_net_settlement"]
        actual_settlement_net = settlement.net_amount if settlement else None
        actual_bank_credit = bank.credit_amount if bank else None
        discrepancy = calc_result["discrepancy_amount"]

        # Check for SLA Delay (Operational latency)
        if settlement and payment.captured_at and settlement.settled_at:
            delay_days = (settlement.settled_at - payment.captured_at).total_seconds() / 86400.0
            if delay_days > sla_delay_threshold_days:
                operational_warning = "SETTLEMENT_DELAY"
                all_signals.append(f"SETTLEMENT_LATENCY_{int(delay_days)}_DAYS")

        # 1. Duplicate Settlement Detection
        if duplicate_settlements:
            all_signals.append("MULTIPLE_SETTLEMENTS_DETECTED")
            return (
                ReconciliationStatus.DUPLICATE,
                "DUPLICATE_SETTLEMENT",
                operational_warning,
                all_signals
            )

        # 2. Missing Settlement Detection
        if settlement is None:
            if matching_method == "AMBIGUOUS_COMPETING_MATCHES":
                all_signals.append("COMPETING_SETTLEMENT_CANDIDATES")
                return (
                    ReconciliationStatus.REVIEW,
                    "REFERENCE_ID_DISCREPANCY",
                    operational_warning,
                    all_signals
                )
            all_signals.append("UNSETTLED_PAYMENT")
            return (
                ReconciliationStatus.MISSING_SETTLEMENT,
                "MISSING_SETTLEMENT",
                operational_warning,
                all_signals
            )

        # 3. Missing Bank Transaction Detection
        if bank is None:
            all_signals.append("SETTLEMENT_UNCREDITED_AT_BANK")
            return (
                ReconciliationStatus.MISSING_BANK_TRANSACTION,
                "MISSING_BANK_TRANSACTION",
                operational_warning,
                all_signals
            )

        # 4. Order vs Payment Amount Mismatch (Partial / Over payment)
        if order and quantize_money(order.total_amount) != quantize_money(payment.amount):
            all_signals.append(f"ORDER_AMOUNT_MISMATCH_EXPECTED_{order.total_amount}_GOT_{payment.amount}")
            return (
                ReconciliationStatus.EXCEPTION,
                "AMOUNT_MISMATCH",
                operational_warning,
                all_signals
            )

        # 5. Reference ID Discrepancy (Altered or non-standard reference format)
        if matching_method == "AMOUNT_PROXIMITY" or "REFERENCE_ID_MISMATCH_DETECTED" in signals:
            all_signals.append("REFERENCE_IDENTIFIER_DISCREPANCY")
            return (
                ReconciliationStatus.EXCEPTION,
                "REFERENCE_ID_DISCREPANCY",
                operational_warning,
                all_signals
            )

        # 6. Fee Mismatch Detection
        total_recorded_fees = sum((f.amount for f in fees), Decimal("0.00"))
        if settlement.fee_amount and quantize_money(settlement.fee_amount) != quantize_money(total_recorded_fees):
            fee_diff = quantize_money(settlement.fee_amount - total_recorded_fees)
            all_signals.append(f"SETTLEMENT_FEE_VARIANCE_{fee_diff}")
            return (
                ReconciliationStatus.EXCEPTION,
                "FEE_MISMATCH",
                operational_warning,
                all_signals
            )

        # 7. Tax Mismatch Detection (GST)
        total_recorded_taxes = sum((t.amount for t in taxes), Decimal("0.00"))
        if settlement.tax_amount is not None and quantize_money(settlement.tax_amount) != quantize_money(total_recorded_taxes):
            tax_diff = quantize_money(settlement.tax_amount - total_recorded_taxes)
            all_signals.append(f"SETTLEMENT_TAX_VARIANCE_{tax_diff}")
            return (
                ReconciliationStatus.EXCEPTION,
                "TAX_MISMATCH",
                operational_warning,
                all_signals
            )

        # 8. Unexplained Financial Variance (Bank / Settlement difference without ledger evidence)
        if discrepancy != Decimal("0.00"):
            all_signals.append(f"UNEXPLAINED_VARIANCE_AMOUNT_{discrepancy}")
            return (
                ReconciliationStatus.EXCEPTION,
                "UNEXPLAINED_EXCEPTION",
                operational_warning,
                all_signals
            )

        # 9. Clean Matched (Clean settlement + bank match)
        if operational_warning == "SETTLEMENT_DELAY":
            return (
                ReconciliationStatus.MATCHED,
                "SETTLEMENT_DELAY",
                operational_warning,
                all_signals
            )

        return (
            ReconciliationStatus.MATCHED,
            "NONE",
            None,
            all_signals
        )
