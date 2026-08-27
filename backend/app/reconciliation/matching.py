from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from app.models.schema import Payment, Settlement, BankTransaction, Order
from app.reconciliation.calculator import quantize_money


class MultiPassMatcher:
    """
    Deterministic Multi-Pass Record Matcher.
    Pass 1: Exact Reference Match
    Pass 2: Direct ID Linkage
    Pass 3: Amount + Timestamp Proximity Window (with Ambiguity Safeguards)
    """

    def __init__(self, proximity_window_days: int = 5):
        self.proximity_window_days = proximity_window_days

    def match_payment_to_settlements(
        self,
        payment: Payment,
        unmatched_settlements: List[Settlement],
        all_settlements_by_payment_id: Dict[str, List[Settlement]]
    ) -> Tuple[Optional[Settlement], List[Settlement], str, float, List[str], Optional[List[Dict[str, Any]]]]:
        """
        Matches a Payment to its Settlement(s).
        Returns:
            (primary_settlement, duplicate_settlements, matching_method, matching_score, signals, competing_candidates)
        """
        signals = []
        competing_candidates = None

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

        # Pass 2: Exact Reference Matching (embedded payment reference in settlement reference)
        for st in unmatched_settlements:
            if st.settlement_reference and payment.payment_reference:
                # Check if payment_reference matches or is a substring of settlement_reference
                clean_pay_ref = payment.payment_reference.replace("PAY_", "")
                if clean_pay_ref in st.settlement_reference or payment.payment_reference == st.settlement_reference:
                    signals.append("EXACT_REFERENCE_MATCH")
                    return (st, [], "EXACT_REFERENCE", 98.0, signals, None)

        # Pass 3: Amount + Timestamp Proximity Window Fallback
        # Candidate must have settlement.gross_amount == payment.amount (or close) and be within time window
        candidates: List[Settlement] = []
        time_start = payment.captured_at
        time_end = payment.captured_at + timedelta(days=self.proximity_window_days + 30) # allow delayed settlements

        for st in unmatched_settlements:
            if st.payment_id and not st.payment_id.startswith("pay_unknown"):
                continue  # Already belongs to another specific payment
            
            amount_matches = (st.gross_amount == payment.amount)
            time_matches = (time_start <= st.settled_at <= time_end)

            if amount_matches and time_matches:
                candidates.append(st)

        if len(candidates) == 1:
            signals.append("PROXIMITY_AMOUNT_TIMESTAMP_MATCH")
            signals.append("REFERENCE_ID_MISMATCH_DETECTED")
            return (candidates[0], [], "AMOUNT_PROXIMITY", 85.0, signals, None)

        elif len(candidates) > 1:
            # Ambiguity Rule: Multiple competing matches exist. Refuse arbitrary selection.
            signals.append("AMBIGUOUS_COMPETING_MATCHES")
            competing_candidates = [
                {
                    "settlement_id": c.id,
                    "settlement_reference": c.settlement_reference,
                    "net_amount": str(c.net_amount),
                    "settled_at": c.settled_at.isoformat(),
                }
                for c in candidates
            ]
            return (None, [], "AMBIGUOUS_COMPETING_MATCHES", 45.0, signals, competing_candidates)

        # No match found
        signals.append("NO_SETTLEMENT_MATCHED")
        return (None, [], "UNMATCHED", 0.0, signals, None)

    def match_settlement_to_bank(
        self,
        settlement: Optional[Settlement],
        all_bank_transactions: List[BankTransaction],
        bank_by_settlement_id: Dict[str, BankTransaction]
    ) -> Tuple[Optional[BankTransaction], str, float, List[str]]:
        """
        Matches a Settlement to its Bank Transaction credit.
        """
        if settlement is None:
            return (None, "UNMATCHED", 0.0, ["SETTLEMENT_IS_NULL"])

        signals = []

        # 1. Direct settlement_id link
        if settlement.id in bank_by_settlement_id:
            signals.append("DIRECT_SETTLEMENT_ID_BANK_MATCH")
            return (bank_by_settlement_id[settlement.id], "DIRECT_ID_LINK", 100.0, signals)

        # 2. Exact UTR / Reference Matching
        clean_set_ref = settlement.settlement_reference.replace("SET_", "")
        for bnk in all_bank_transactions:
            if clean_set_ref in bnk.bank_reference or (bnk.utr_number and clean_set_ref in bnk.utr_number):
                signals.append("BANK_REFERENCE_EXACT_MATCH")
                return (bnk, "EXACT_REFERENCE", 95.0, signals)

        # 3. Fallback Amount + Date Proximity matching
        candidates = []
        for bnk in all_bank_transactions:
            if bnk.settlement_id is None or bnk.settlement_id == settlement.id:
                if bnk.credit_amount == settlement.net_amount:
                    time_diff = abs((bnk.transaction_date - settlement.settled_at).total_seconds())
                    if time_diff <= 86400 * 3:  # within 3 days
                        candidates.append(bnk)

        if len(candidates) == 1:
            signals.append("BANK_AMOUNT_PROXIMITY_MATCH")
            return (candidates[0], "AMOUNT_PROXIMITY", 85.0, signals)
        elif len(candidates) > 1:
            signals.append("AMBIGUOUS_BANK_RECORDS")
            return (candidates[0], "AMBIGUOUS_COMPETING_MATCHES", 50.0, signals)

        signals.append("MISSING_BANK_TRANSACTION_RECORD")
        return (None, "UNMATCHED", 0.0, signals)
