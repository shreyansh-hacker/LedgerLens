from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from app.models.schema import Fee, Tax, Refund


def quantize_money(amount: Decimal) -> Decimal:
    """Ensure exact 2-decimal-place precision using ROUND_HALF_UP."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FinancialCalculator:
    """
    Deterministic Financial Calculation Engine.
    Computes exact expected settlements, bank amounts, and variances
    using Python Decimal (never float).
    """

    GST_RATE = Decimal("0.18")

    @classmethod
    def calculate_expected_settlement(
        cls,
        payment_amount: Decimal,
        fees: List[Fee],
        taxes: List[Tax],
        refunds: Optional[List[Refund]] = None,
        adjustments: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Formula:
        expected_net_settlement = payment_amount - sum(fees) - sum(taxes) - sum(refunds) + adjustments
        """
        total_fees = sum((quantize_money(f.amount) for f in fees), Decimal("0.00"))
        total_taxes = sum((quantize_money(t.amount) for t in taxes), Decimal("0.00"))
        
        total_refunds = Decimal("0.00")
        if refunds:
            total_refunds = sum((quantize_money(r.amount) for r in refunds), Decimal("0.00"))

        net_adjustments = adjustments if adjustments is not None else Decimal("0.00")

        expected_net = quantize_money(
            payment_amount - total_fees - total_taxes - total_refunds + net_adjustments
        )

        return {
            "payment_gross": quantize_money(payment_amount),
            "total_fees": quantize_money(total_fees),
            "total_taxes": quantize_money(total_taxes),
            "total_refunds": quantize_money(total_refunds),
            "adjustments": quantize_money(net_adjustments),
            "expected_net_settlement": expected_net,
            "expected_bank_amount": expected_net,
        }

    @classmethod
    def calculate_discrepancy(
        cls,
        expected_settlement: Decimal,
        actual_settlement_net: Optional[Decimal],
        actual_bank_credit: Optional[Decimal]
    ) -> Dict[str, Any]:
        """
        Calculates discrepancies between expectation and actual bank/settlement reality.
        """
        if actual_bank_credit is not None:
            diff = quantize_money(expected_settlement - actual_bank_credit)
        elif actual_settlement_net is not None:
            diff = quantize_money(expected_settlement - actual_settlement_net)
        else:
            diff = quantize_money(expected_settlement)

        settlement_variance = Decimal("0.00")
        if actual_settlement_net is not None:
            settlement_variance = quantize_money(expected_settlement - actual_settlement_net)

        bank_settlement_variance = Decimal("0.00")
        if actual_settlement_net is not None and actual_bank_credit is not None:
            bank_settlement_variance = quantize_money(actual_settlement_net - actual_bank_credit)

        return {
            "discrepancy_amount": diff,
            "settlement_variance": settlement_variance,
            "bank_settlement_variance": bank_settlement_variance,
            "has_discrepancy": diff != Decimal("0.00"),
        }
