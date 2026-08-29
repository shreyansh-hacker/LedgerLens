from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from app.models.schema import Payment, Settlement, BankTransaction, Order
from app.reconciliation.calculator import quantize_money


class MultiPassMatcher:
    """
    Deterministic Multi-Pass Record Matcher.
    Pass 1: Direct ID Linkage
    Pass 2: Exact Reference Match (Indexed)
    Pass 3: Amount + Timestamp Proximity Window (with Ambiguity Safeguards)
    """

    def __init__(self, proximity_window_days: int = 5):
        self.proximity_window_days = proximity_window_days

    def match_payment_to_settlements(
        self,
        payment: Payment,
        unmatched_settlements: List[Settlement],
        all_settlements_by_payment_id: Dict[str, List[Settlement]],
        settlements_by_ref: Optional[Dict[str, Settlement]] = None,
    ) -> Tuple[Optional[Settlement], List[Settlement], str, float, List[str], Optional[List[Dict[str, Any]]]]:
        """
        Matches a Payment to its Settlement(s).
        Returns:
            (primary_settlement, duplicate_settlements, matching_method, matching_score, signals, competing_candidates)
        """
        signals = []

        # Check for duplicate settlements attached directly to this payment ID
        direct_settlements = all_settlements_by_payment_id.get(payment.id, [])
        if len(direct_settlements) > 1:
            signals.append("DUPLICATE_SETTLEMENT_RECORDS_DETECTED")
            return (
                direct_settlements[0],
                direct_settlements[1:],
                "DIRECT_ID_LINK",
                95.0,
                signals,
                None
            )

        # Pass 1: Direct ID Link (settlement.payment_id == payment.id)
        if len(direct_settlements) == 1:
            st = direct_settlements[0]
            signals.append("DIRECT_PAYMENT_ID_LINK")
            return (st, [], "DIRECT_ID_LINK", 100.0, signals, None)

        # Pass 2: Fast Exact Reference Matching
        if payment.payment_reference:
            clean_pay_ref = payment.payment_reference.replace("PAY_", "")
            if settlements_by_ref and clean_pay_ref in settlements_by_ref:
                st = settlements_by_ref[clean_pay_ref]
                signals.append("EXACT_REFERENCE_MATCH")
                return (st, [], "EXACT_REFERENCE", 98.0, signals, None)

            for st in unmatched_settlements:
                if st.settlement_reference and (clean_pay_ref in st.settlement_reference or payment.payment_reference == st.settlement_reference):
                    signals.append("EXACT_REFERENCE_MATCH")
                    return (st, [], "EXACT_REFERENCE", 98.0, signals, None)

        # Pass 3: Amount + Timestamp Proximity Window Fallback
        candidates: List[Settlement] = []
        time_start = payment.captured_at
        time_end = payment.captured_at + timedelta(days=self.proximity_window_days + 30)

        for st in unmatched_settlements:
            if st.payment_id and not st.payment_id.startswith("pay_unknown"):
                continue  # Already belongs to another specific payment

            diff = abs(payment.amount - st.gross_amount)
            if diff <= Decimal("0.05") and time_start <= st.settled_at <= time_end:
                candidates.append(st)

        if not candidates:
            return (None, [], "UNMATCHED", 0.0, ["NO_MATCHING_SETTLEMENT_FOUND"], None)

        if len(candidates) == 1:
            signals.append("PROXIMITY_WINDOW_MATCH")
            return (candidates[0], [], "AMOUNT_PROXIMITY", 85.0, signals, None)

        # Ambiguity Safeguard
        competing_candidates = [
            {"settlement_id": c.id, "amount": str(c.gross_amount), "settled_at": c.settled_at.isoformat()}
            for c in candidates
        ]
        signals.append("AMBIGUOUS_CANDIDATES_DETECTED")
        return (None, [], "AMBIGUOUS_COMPETING_MATCHES", 40.0, signals, competing_candidates)

    def match_settlement_to_bank(
        self,
        settlement: Optional[Settlement],
        all_bank_transactions: List[BankTransaction],
        bank_by_settlement_id: Dict[str, BankTransaction],
        bank_by_reference: Optional[Dict[str, BankTransaction]] = None,
    ) -> Tuple[Optional[BankTransaction], str, float, List[str]]:
        """
        Matches a Settlement to its Bank Transaction.
        """
        if not settlement:
            return (None, "UNMATCHED", 0.0, ["NO_SETTLEMENT_FOR_BANK_MATCH"])

        signals = []

        # Pass 1: Direct Link (bank.settlement_id == settlement.id)
        if settlement.id in bank_by_settlement_id:
            signals.append("DIRECT_SETTLEMENT_ID_LINK")
            return (bank_by_settlement_id[settlement.id], "DIRECT_ID_LINK", 100.0, signals)

        # Pass 2: Exact Reference Match
        if settlement.settlement_reference:
            clean_set_ref = settlement.settlement_reference.replace("SET_", "")
            if bank_by_reference and clean_set_ref in bank_by_reference:
                signals.append("EXACT_REFERENCE_MATCH")
                return (bank_by_reference[clean_set_ref], "EXACT_REFERENCE", 98.0, signals)

            for b in all_bank_transactions:
                if b.bank_reference and clean_set_ref in b.bank_reference:
                    signals.append("EXACT_REFERENCE_MATCH")
                    return (b, "EXACT_REFERENCE", 98.0, signals)

        # Pass 3: Amount + Timestamp Proximity Window
        candidates = []
        time_start = settlement.settled_at
        time_end = settlement.settled_at + timedelta(days=self.proximity_window_days + 15)

        for b in all_bank_transactions:
            if b.settlement_id:
                continue
            diff = abs(settlement.net_amount - b.credit_amount)
            if diff <= Decimal("0.05") and time_start <= b.transaction_date <= time_end:
                candidates.append(b)

        if not candidates:
            signals.append("MISSING_BANK_CREDIT_TRANSACTION")
            return (None, "UNMATCHED", 0.0, signals)

        if len(candidates) == 1:
            signals.append("PROXIMITY_WINDOW_MATCH")
            return (candidates[0], "AMOUNT_PROXIMITY", 85.0, signals)

        signals.append("AMBIGUOUS_BANK_CANDIDATES")
        return (None, "UNMATCHED_AMBIGUOUS", 40.0, signals)
