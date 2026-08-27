import random
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from app.synthetic.scenarios import (
    ScenarioType,
    GroundTruthMetadata,
    DEFAULT_SCENARIO_DISTRIBUTION,
)


def quantize_money(amount: Decimal) -> Decimal:
    """Ensure exact 2-decimal-place precision using ROUND_HALF_UP."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class SyntheticFinancialDataEngine:
    """
    Deterministic Synthetic Financial Data Generator.
    Generates realistic merchant transaction clusters across:
    Merchant -> Order -> Payment -> Fees/Tax/Refunds -> Settlement -> Bank Transaction
    along with controlled Ground Truth metadata for evaluation.
    """

    MERCHANT_PROFILES = [
        {"id": "mer_nova_01", "name": "NovaRetail India", "email": "finance@novaretail.in"},
        {"id": "mer_apex_02", "name": "ApexKart Global", "email": "accounts@apexkart.com"},
        {"id": "mer_zenith_03", "name": "Zenith Commerce", "email": "settlements@zenith.in"},
        {"id": "mer_pulse_04", "name": "PulsePay Merchants", "email": "ops@pulsepay.in"},
        {"id": "mer_craft_05", "name": "CraftVilla Traders", "email": "treasury@craftvilla.org"},
    ]

    PAYMENT_METHODS = [
        {"method": "UPI", "weight": 0.50, "fee_rate": Decimal("0.0020")},      # 0.20%
        {"method": "CREDIT_CARD", "weight": 0.25, "fee_rate": Decimal("0.0195")}, # 1.95%
        {"method": "DEBIT_CARD", "weight": 0.15, "fee_rate": Decimal("0.0090")},  # 0.90%
        {"method": "NET_BANKING", "weight": 0.10, "fee_rate": Decimal("0.0150")}, # 1.50%
    ]

    GST_RATE = Decimal("0.18")  # Standard 18% GST on processing fees

    def __init__(
        self,
        seed: int = 42,
        scenario_distribution: Optional[Dict[ScenarioType, float]] = None,
        base_start_date: Optional[datetime] = None,
    ):
        self.seed = seed
        self.rng = random.Random(seed)
        self.distribution = scenario_distribution or DEFAULT_SCENARIO_DISTRIBUTION
        self.base_date = base_start_date or datetime(2026, 7, 1, 9, 0, 0)
        self._validate_distribution()

    def _validate_distribution(self):
        total_prob = sum(self.distribution.values())
        if not (0.999 <= total_prob <= 1.001):
            raise ValueError(f"Scenario distribution probabilities must sum to 1.0, got {total_prob}")

    def _sample_scenario(self) -> ScenarioType:
        scenarios = list(self.distribution.keys())
        weights = list(self.distribution.values())
        return self.rng.choices(scenarios, weights=weights, k=1)[0]

    def _generate_amount(self) -> Decimal:
        """Sample realistic order amount distributions (₹100 to ₹120,000)."""
        tier = self.rng.choices(
            ["micro", "small", "medium", "large", "enterprise"],
            weights=[0.20, 0.35, 0.30, 0.12, 0.03],
            k=1
        )[0]

        if tier == "micro":
            cents = self.rng.randint(10000, 99900)  # ₹100.00 to ₹999.00
        elif tier == "small":
            cents = self.rng.randint(100000, 499900)  # ₹1,000.00 to ₹4,999.00
        elif tier == "medium":
            cents = self.rng.randint(500000, 1999900)  # ₹5,000.00 to ₹19,999.00
        elif tier == "large":
            cents = self.rng.randint(2000000, 4999900)  # ₹20,000.00 to ₹49,999.00
        else:
            cents = self.rng.randint(5000000, 12000000)  # ₹50,000.00 to ₹120,000.00

        return quantize_money(Decimal(cents) / Decimal(100))

    def _sample_payment_method(self) -> Dict[str, Any]:
        methods = self.PAYMENT_METHODS
        weights = [m["weight"] for m in methods]
        return self.rng.choices(methods, weights=weights, k=1)[0]

    def generate_dataset(
        self,
        num_clusters: int = 1000,
        merchant_count: int = 5
    ) -> Dict[str, Any]:
        """
        Generates complete financial clusters + ground truth records.
        """
        merchants = self.MERCHANT_PROFILES[:merchant_count]
        
        orders: List[Dict[str, Any]] = []
        payments: List[Dict[str, Any]] = []
        fees: List[Dict[str, Any]] = []
        taxes: List[Dict[str, Any]] = []
        refunds: List[Dict[str, Any]] = []
        settlements: List[Dict[str, Any]] = []
        bank_transactions: List[Dict[str, Any]] = []
        ground_truth: List[Dict[str, Any]] = []

        for idx in range(1, num_clusters + 1):
            merchant = self.rng.choice(merchants)
            scenario = self._sample_scenario()
            cluster_id = f"CLU_{idx:05d}"
            
            # Base timestamps
            time_offset_hours = idx * 0.75 + self.rng.uniform(0.1, 0.9)
            order_time = self.base_date + timedelta(hours=time_offset_hours)
            payment_time = order_time + timedelta(minutes=self.rng.randint(2, 12))
            
            # Financial baseline
            order_amount = self._generate_amount()
            pm_info = self._sample_payment_method()
            payment_method = pm_info["method"]
            fee_rate = pm_info["fee_rate"]

            # Compute standard deterministic fee and tax
            base_fee = quantize_money(order_amount * fee_rate)
            if fee_rate > 0 and base_fee < Decimal("2.00"):
                base_fee = Decimal("2.00")
            
            base_tax = quantize_money(base_fee * self.GST_RATE)
            refund_amount = Decimal("0.00")

            # Standard expected settlement amount
            expected_settlement_amount = quantize_money(
                order_amount - base_fee - base_tax - refund_amount
            )
            expected_bank_amount = expected_settlement_amount

            # Generate entity IDs
            ord_id = f"ord_{idx:05d}"
            ord_ref = f"ORD_{order_time.strftime('%Y%m%d')}_{idx:05d}"
            
            pay_id = f"pay_{idx:05d}"
            pay_ref = f"PAY_{payment_time.strftime('%Y%m%d')}_{idx:05d}"
            
            fee_id = f"fee_{idx:05d}"
            tax_id = f"tax_{idx:05d}"
            set_id = f"set_{idx:05d}"
            set_ref = f"SET_{payment_time.strftime('%Y%m%d')}_{idx:05d}"
            
            bnk_id = f"bnk_{idx:05d}"
            bnk_ref = f"BNK_{payment_time.strftime('%Y%m%d')}_{idx:05d}"
            utr_num = f"UTR{payment_time.strftime('%Y%m%d')}{idx:06d}"

            # Standard timestamps for downstream records
            settlement_time = payment_time + timedelta(days=self.rng.randint(1, 2))
            bank_time = settlement_time + timedelta(hours=self.rng.randint(2, 6))

            # Default entities
            order_obj = {
                "id": ord_id,
                "merchant_id": merchant["id"],
                "order_reference": ord_ref,
                "customer_id": f"cust_{self.rng.randint(1000, 9999)}",
                "total_amount": order_amount,
                "currency": "INR",
                "status": "COMPLETED",
                "created_at": order_time,
            }

            payment_obj = {
                "id": pay_id,
                "order_id": ord_id,
                "payment_reference": pay_ref,
                "gateway_name": "Razorpay",
                "amount": order_amount,
                "currency": "INR",
                "method": payment_method,
                "status": "captured",
                "captured_at": payment_time,
            }

            fee_obj = {
                "id": fee_id,
                "payment_id": pay_id,
                "fee_type": f"{payment_method.lower()}_processing_fee",
                "rate_percentage": quantize_money(fee_rate * Decimal("100")),
                "amount": base_fee,
                "currency": "INR",
                "created_at": payment_time,
            }

            tax_obj = {
                "id": tax_id,
                "payment_id": pay_id,
                "tax_type": "GST_18",
                "rate_percentage": Decimal("18.00"),
                "amount": base_tax,
                "currency": "INR",
                "created_at": payment_time,
            }

            settlement_obj: Optional[Dict[str, Any]] = {
                "id": set_id,
                "payment_id": pay_id,
                "settlement_reference": set_ref,
                "gross_amount": order_amount,
                "fee_amount": base_fee,
                "tax_amount": base_tax,
                "net_amount": expected_settlement_amount,
                "currency": "INR",
                "status": "settled",
                "settled_at": settlement_time,
            }

            bank_obj: Optional[Dict[str, Any]] = {
                "id": bnk_id,
                "settlement_id": set_id,
                "bank_reference": bnk_ref,
                "account_number_mask": "XX" + str(self.rng.randint(1000, 9999)),
                "credit_amount": expected_bank_amount,
                "currency": "INR",
                "utr_number": utr_num,
                "transaction_date": bank_time,
            }

            # Ground truth defaults
            gt_status = "MATCHED"
            gt_diff = Decimal("0.00")
            gt_reason = "Transaction reconciled cleanly across payment, fees, settlement, and bank credit."
            gt_auto_resolve = True
            gt_human_review = False
            gt_explainable = True
            gt_signals = ["EXACT_ID_MATCH", "AMOUNT_MATCH", "TAX_VERIFIED", "BANK_UTR_VERIFIED"]

            # Apply Controlled Ground-Truth Scenarios
            if scenario == ScenarioType.NORMAL_MATCH:
                pass  # Clean standard match

            elif scenario == ScenarioType.FEE_MISMATCH:
                # Actual settlement deducted higher fee than scheduled
                fee_surge = quantize_money(base_fee * Decimal("1.50") + Decimal("50.00"))
                actual_tax = quantize_money(fee_surge * self.GST_RATE)
                actual_net = quantize_money(order_amount - fee_surge - actual_tax)
                
                settlement_obj["fee_amount"] = fee_surge
                settlement_obj["tax_amount"] = actual_tax
                settlement_obj["net_amount"] = actual_net
                bank_obj["credit_amount"] = actual_net
                
                gt_diff = quantize_money(expected_settlement_amount - actual_net)
                gt_status = "EXCEPTION"
                gt_reason = f"Gateway settlement fee deducted (₹{fee_surge}) was higher than scheduled fee (₹{base_fee})."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["FEE_DISCREPANCY", "SETTLEMENT_VARIANCE"]

            elif scenario == ScenarioType.TAX_MISMATCH:
                # Gateway omitted or calculated wrong GST
                wrong_tax = Decimal("0.00")
                actual_net = quantize_money(order_amount - base_fee - wrong_tax)
                
                settlement_obj["tax_amount"] = wrong_tax
                settlement_obj["net_amount"] = actual_net
                bank_obj["credit_amount"] = actual_net
                
                gt_diff = quantize_money(expected_settlement_amount - actual_net)
                gt_status = "EXCEPTION"
                gt_reason = f"GST tax deducted in settlement (₹{wrong_tax}) differs from expected 18% GST (₹{base_tax})."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["TAX_RATE_MISMATCH", "SETTLEMENT_VARIANCE"]

            elif scenario == ScenarioType.MISSING_BANK_TRANSACTION:
                # Bank credit missing
                bank_obj = None
                gt_diff = expected_bank_amount
                gt_status = "EXCEPTION"
                gt_reason = "Settlement was processed by gateway but bank statement credit is missing."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["MISSING_BANK_RECORD", "UNCREDITED_SETTLEMENT"]

            elif scenario == ScenarioType.MISSING_SETTLEMENT:
                # Settlement and bank missing
                settlement_obj = None
                bank_obj = None
                gt_diff = expected_settlement_amount
                gt_status = "EXCEPTION"
                gt_reason = "Payment captured but settlement batch was not created by payment gateway."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["MISSING_SETTLEMENT", "UNSETTLED_PAYMENT"]

            elif scenario == ScenarioType.DUPLICATE_SETTLEMENT:
                # Duplicate settlement
                dup_set_id = f"set_dup_{idx:05d}"
                dup_set_ref = f"SET_DUP_{payment_time.strftime('%Y%m%d')}_{idx:05d}"
                dup_settlement = {
                    "id": dup_set_id,
                    "payment_id": pay_id,
                    "settlement_reference": dup_set_ref,
                    "gross_amount": order_amount,
                    "fee_amount": base_fee,
                    "tax_amount": base_tax,
                    "net_amount": expected_settlement_amount,
                    "currency": "INR",
                    "status": "settled",
                    "settled_at": settlement_time + timedelta(hours=12),
                }
                settlements.append(dup_settlement)
                
                gt_diff = -expected_settlement_amount
                gt_status = "EXCEPTION"
                gt_reason = "Duplicate settlement records found referencing identical payment ID."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["DUPLICATE_SETTLEMENT", "DOUBLE_CREDIT_RISK"]

            elif scenario == ScenarioType.REFERENCE_ID_DISCREPANCY:
                # Altered reference ID
                altered_ref = f"SET_EXT_ERR_{idx:05d}"
                settlement_obj["settlement_reference"] = altered_ref
                settlement_obj["payment_id"] = f"pay_unknown_{idx:05d}"
                
                gt_diff = Decimal("0.00")
                gt_status = "EXCEPTION"
                gt_reason = "Payment reference mismatch between gateway event and settlement batch."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["REFERENCE_ID_MISMATCH", "FUZZY_MATCH_REQUIRED"]

            elif scenario == ScenarioType.AMOUNT_MISMATCH:
                # Payment captured was lower than order
                partial_payment = quantize_money(order_amount * Decimal("0.80"))
                payment_obj["amount"] = partial_payment
                
                partial_fee = quantize_money(partial_payment * fee_rate)
                if fee_rate > 0 and partial_fee < Decimal("2.00"):
                    partial_fee = Decimal("2.00")
                partial_tax = quantize_money(partial_fee * self.GST_RATE)
                partial_net = quantize_money(partial_payment - partial_fee - partial_tax)
                
                fee_obj["amount"] = partial_fee
                tax_obj["amount"] = partial_tax
                settlement_obj["gross_amount"] = partial_payment
                settlement_obj["fee_amount"] = partial_fee
                settlement_obj["tax_amount"] = partial_tax
                settlement_obj["net_amount"] = partial_net
                bank_obj["credit_amount"] = partial_net

                expected_settlement_amount = partial_net
                expected_bank_amount = partial_net
                
                gt_diff = quantize_money(order_amount - partial_payment)
                gt_status = "EXCEPTION"
                gt_reason = f"Payment captured (₹{partial_payment}) was less than total order value (₹{order_amount})."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = True
                gt_signals = ["ORDER_PAYMENT_MISMATCH", "PARTIAL_CAPTURE"]

            elif scenario == ScenarioType.SETTLEMENT_DELAY:
                # Delayed settlement
                delayed_days = self.rng.randint(18, 28)
                delayed_settlement_time = payment_time + timedelta(days=delayed_days)
                delayed_bank_time = delayed_settlement_time + timedelta(hours=4)
                
                settlement_obj["settled_at"] = delayed_settlement_time
                bank_obj["transaction_date"] = delayed_bank_time
                
                gt_diff = Decimal("0.00")
                gt_status = "MATCHED"
                gt_reason = f"Amounts reconcile perfectly, but settlement latency ({delayed_days} days) exceeded SLA."
                gt_auto_resolve = True
                gt_human_review = False
                gt_explainable = True
                gt_signals = ["SETTLEMENT_LATENCY_ANOMALY", "SLA_BREACH"]

            elif scenario == ScenarioType.UNEXPLAINED_EXCEPTION:
                # Unexplained discrepancy
                unexplained_cut = quantize_money(
                    order_amount * Decimal(self.rng.uniform(0.10, 0.35)) + Decimal("150.00")
                )
                actual_net = quantize_money(expected_settlement_amount - unexplained_cut)
                
                settlement_obj["net_amount"] = actual_net
                bank_obj["credit_amount"] = actual_net
                
                gt_diff = unexplained_cut
                gt_status = "EXCEPTION"
                gt_reason = f"Unexplained financial variance of ₹{unexplained_cut} with zero supporting fee, tax, or refund records."
                gt_auto_resolve = False
                gt_human_review = True
                gt_explainable = False
                gt_signals = ["UNEXPLAINED_VARIANCE", "NO_LEDGER_EVIDENCE"]

            # Append entities
            orders.append(order_obj)
            payments.append(payment_obj)
            fees.append(fee_obj)
            taxes.append(tax_obj)
            if settlement_obj is not None:
                settlements.append(settlement_obj)
            if bank_obj is not None:
                bank_transactions.append(bank_obj)

            # Ground Truth record
            gt_record = GroundTruthMetadata(
                cluster_id=cluster_id,
                scenario_type=scenario,
                expected_status=gt_status,
                expected_settlement_amount=expected_settlement_amount,
                expected_bank_amount=expected_bank_amount,
                expected_difference=gt_diff,
                expected_reason=gt_reason,
                should_auto_resolve=gt_auto_resolve,
                should_require_human_review=gt_human_review,
                is_explainable=gt_explainable,
                discrepancy_signals=gt_signals,
            )
            ground_truth.append(gt_record.model_dump())

        return {
            "merchants": merchants,
            "orders": orders,
            "payments": payments,
            "fees": fees,
            "taxes": taxes,
            "refunds": refunds,
            "settlements": settlements,
            "bank_transactions": bank_transactions,
            "ground_truth": ground_truth,
        }
