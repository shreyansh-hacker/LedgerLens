from typing import List, Dict, Any


class AnomalySignalGenerator:
    """
    Generates human-readable observable anomaly explanation signals.
    Provides transparent reasoning regarding contributing feature deviations.
    """

    @classmethod
    def generate_signals(
        cls,
        features: Dict[str, Any],
        raw_score: float,
        normalized_score: float
    ) -> List[str]:
        signals = []

        # 1. Transaction Amount Signals
        amt_ratio = features.get("amount_ratio_to_merchant_median", 1.0)
        pay_amt = features.get("payment_amount", 0.0)
        if amt_ratio >= 4.0:
            signals.append(f"Payment amount (₹{pay_amt:,.2f}) is {amt_ratio:.1f}× higher than merchant median baseline.")
        elif amt_ratio <= 0.15 and pay_amt < 200.0:
            signals.append(f"Micro-transaction amount (₹{pay_amt:,.2f}) is unusually small for merchant profile.")

        # 2. Fee Ratio Deviations
        fee_ratio = features.get("fee_to_amount_ratio", 0.0)
        if fee_ratio > 0.035:
            signals.append(f"Fee deduction ratio ({fee_ratio*100:.2f}%) exceeds standard gateway rate schedule.")

        # 3. Tax / GST Deviations
        tax_ratio = features.get("tax_to_fee_ratio", 0.18)
        if tax_ratio < 0.05:
            signals.append("Zero/negligible GST recorded on gateway processing fees.")
        elif tax_ratio > 0.30:
            signals.append(f"Tax-to-fee ratio ({tax_ratio*100:.1f}%) exceeds standard 18% GST rate.")

        # 4. Discrepancy Magnitude
        disc_ratio = features.get("discrepancy_to_amount_ratio", 0.0)
        if disc_ratio >= 0.10:
            signals.append(f"Financial discrepancy accounts for {disc_ratio*100:.1f}% of total transaction value.")

        # 5. Timing Latencies
        set_delay_hours = features.get("settlement_delay_hours", 0.0)
        if set_delay_hours > 24.0 * 7:  # > 7 days
            delay_days = set_delay_hours / 24.0
            signals.append(f"Settlement latency ({delay_days:.1f} days) severely breaches normal gateway SLA window.")

        # 6. Structural Discrepancies
        if features.get("is_settlement_missing", 0.0) == 1.0:
            signals.append("Payment captured but gateway settlement batch record is missing.")
        if features.get("is_bank_missing", 0.0) == 1.0:
            signals.append("Settlement processed but corresponding bank statement credit is missing.")
        if features.get("is_duplicate", 0.0) == 1.0:
            signals.append("Multiple duplicate settlement records detected for identical payment.")

        # If high normalized score but few rule signals, flag multi-dimensional feature outlier
        if normalized_score >= 70.0 and len(signals) == 0:
            signals.append("Multi-dimensional feature vector lies on the statistical boundary of the transaction population.")

        return signals
