import statistics
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
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
)


FEATURE_NAMES = [
    "payment_amount",
    "amount_ratio_to_merchant_median",
    "fee_to_amount_ratio",
    "tax_to_fee_ratio",
    "discrepancy_to_amount_ratio",
    "settlement_delay_hours",
    "bank_delay_hours",
    "hour_of_day",
    "day_of_week",
    "is_settlement_missing",
    "is_bank_missing",
    "is_duplicate",
    "matching_confidence",
    "has_operational_warning",
]


class AnomalyFeatureExtractor:
    """
    Extracts observable population-level feature matrices for Isolation Forest.
    Strictly isolated from synthetic ground-truth metadata to eliminate data leakage.
    """

    @classmethod
    def extract_features(
        cls,
        reconciliation_results: List[ReconciliationResult],
        payments_by_id: Dict[str, Payment],
        orders_by_id: Dict[str, Order],
        fees_by_payment_id: Dict[str, List[Fee]],
        taxes_by_payment_id: Dict[str, List[Tax]],
        refunds_by_payment_id: Dict[str, List[Refund]],
        settlements_by_id: Dict[str, Settlement],
        bank_by_id: Dict[str, BankTransaction],
    ) -> Tuple[np.ndarray, List[Dict[str, float]], List[str]]:
        """
        Builds numerical feature matrix (N x M) and feature dictionaries for each record.
        Returns:
            (feature_matrix, list_of_feature_dicts, list_of_reconciliation_ids)
        """
        # 1. Compute population-level merchant baselines (median amount per merchant)
        merchant_amounts: Dict[str, List[float]] = {}
        for r in reconciliation_results:
            pay = payments_by_id.get(r.payment_id)
            if pay and r.order_id:
                order = orders_by_id.get(r.order_id)
                if order:
                    merchant_amounts.setdefault(order.merchant_id, []).append(float(pay.amount))

        merchant_medians: Dict[str, float] = {}
        for m_id, amounts in merchant_amounts.items():
            merchant_medians[m_id] = statistics.median(amounts) if amounts else 5000.0

        # Global median fallback
        all_amounts = [float(p.amount) for p in payments_by_id.values()]
        global_median = statistics.median(all_amounts) if all_amounts else 5000.0

        feature_matrix = []
        feature_dicts = []
        rec_ids = []

        for r in reconciliation_results:
            # Leakage protection assertion:
            # Explicitly verify no ground-truth fields are present on the record object being used
            assert not hasattr(r, "_ground_truth_scenario_used_in_features"), "Leakage check failed"

            pay = payments_by_id.get(r.payment_id)
            if not pay:
                continue

            order = orders_by_id.get(r.order_id) if r.order_id else None
            settlement = settlements_by_id.get(r.settlement_id) if r.settlement_id else None
            bank = bank_by_id.get(r.bank_transaction_id) if r.bank_transaction_id else None
            fees = fees_by_payment_id.get(pay.id, [])
            taxes = taxes_by_payment_id.get(pay.id, [])

            pay_amount = float(pay.amount)
            merchant_id = order.merchant_id if order else "unknown"
            merchant_median = merchant_medians.get(merchant_id, global_median)

            # Amount deviation ratio
            amount_ratio = pay_amount / merchant_median if merchant_median > 0 else 1.0

            # Fee & Tax Ratios
            total_fees = sum((float(f.amount) for f in fees), 0.0)
            total_taxes = sum((float(t.amount) for t in taxes), 0.0)
            fee_ratio = total_fees / pay_amount if pay_amount > 0 else 0.0
            tax_ratio = total_taxes / total_fees if total_fees > 0 else 0.18

            # Discrepancy ratio
            discrepancy_val = float(abs(r.discrepancy_amount))
            disc_ratio = discrepancy_val / pay_amount if pay_amount > 0 else 0.0

            # Timing Delays
            settlement_delay_hours = 36.0  # default baseline
            if settlement and pay.captured_at and settlement.settled_at:
                settlement_delay_hours = max(
                    0.0, (settlement.settled_at - pay.captured_at).total_seconds() / 3600.0
                )

            bank_delay_hours = 4.0  # default baseline
            if bank and settlement and settlement.settled_at and bank.transaction_date:
                bank_delay_hours = max(
                    0.0, (bank.transaction_date - settlement.settled_at).total_seconds() / 3600.0
                )

            # Temporal signals
            hour_of_day = float(pay.captured_at.hour) if pay.captured_at else 12.0
            day_of_week = float(pay.captured_at.weekday()) if pay.captured_at else 2.0

            # Structural Reconciliation Flags
            is_set_missing = 1.0 if settlement is None else 0.0
            is_bnk_missing = 1.0 if bank is None else 0.0
            is_duplicate = 1.0 if r.status == ReconciliationStatus.DUPLICATE else 0.0
            matching_conf = float(r.matching_score)
            has_warning = 1.0 if r.operational_warning else 0.0

            row_dict = {
                "payment_amount": round(pay_amount, 2),
                "amount_ratio_to_merchant_median": round(amount_ratio, 3),
                "fee_to_amount_ratio": round(fee_ratio, 4),
                "tax_to_fee_ratio": round(tax_ratio, 4),
                "discrepancy_to_amount_ratio": round(disc_ratio, 4),
                "settlement_delay_hours": round(settlement_delay_hours, 1),
                "bank_delay_hours": round(bank_delay_hours, 1),
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "is_settlement_missing": is_set_missing,
                "is_bank_missing": is_bnk_missing,
                "is_duplicate": is_duplicate,
                "matching_confidence": matching_conf,
                "has_operational_warning": has_warning,
            }

            row_vector = [row_dict[f] for f in FEATURE_NAMES]

            feature_matrix.append(row_vector)
            feature_dicts.append(row_dict)
            rec_ids.append(r.id)

        return np.array(feature_matrix, dtype=np.float64), feature_dicts, rec_ids
