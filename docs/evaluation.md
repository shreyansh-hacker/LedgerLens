# LedgerLens Evaluation & Ground-Truth Methodology

## 1. Synthetic Financial Dataset Architecture

The LedgerLens synthetic dataset engine (`SyntheticFinancialDataEngine`) generates realistic merchant transaction clusters modeling end-to-end Indian digital commerce flows:

```
Merchant
  ↓
Order (ORD-*)
  ↓
Payment (PAY-* via UPI / Credit Card / Debit Card / Net Banking)
  ↓
Fee (MDR) + GST (18%) + Refunds
  ↓
Settlement (SET-* net calculation)
  ↓
Bank Transaction (BNK-* UTR credit)
```

Every monetary amount uses exact `Decimal` precision with 2 decimal places (`quantize(Decimal("0.01"), ROUND_HALF_UP)`).

---

## 2. Controlled Ground-Truth Scenarios

The engine generates 10 distinct, controlled scenarios with known mathematical truth:

| Scenario Code | Target Distribution | Description | Expected Status | Explainable? | Human Review? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `NORMAL_MATCH` | ~60% | Clean payment, fee, GST, settlement, and bank UTR credit matching. | `MATCHED` | Yes | No |
| `FEE_MISMATCH` | ~8% | Gateway deducted higher fee than scheduled rate. | `EXCEPTION` | Yes | Yes |
| `TAX_MISMATCH` | ~5% | Gateway omitted or miscalculated 18% GST on fees. | `EXCEPTION` | Yes | Yes |
| `MISSING_BANK_TRANSACTION` | ~5% | Settlement created by gateway but no bank credit found. | `EXCEPTION` | Yes | Yes |
| `MISSING_SETTLEMENT` | ~4% | Payment captured but gateway never generated settlement. | `EXCEPTION` | Yes | Yes |
| `DUPLICATE_SETTLEMENT` | ~4% | Double settlement records referencing identical payment. | `EXCEPTION` | Yes | Yes |
| `REFERENCE_ID_DISCREPANCY` | ~4% | Identifier reference mismatch between payment and settlement. | `EXCEPTION` | Yes | Yes |
| `AMOUNT_MISMATCH` | ~4% | Partial payment capture / order amount variance. | `EXCEPTION` | Yes | Yes |
| `SETTLEMENT_DELAY` | ~3% | Settlement occurred 18–28 days after capture (latency anomaly). | `MATCHED` | Yes | No |
| `UNEXPLAINED_EXCEPTION` | ~3% | Financial variance with zero supporting fee, tax, or refund evidence. | `EXCEPTION` | **No** | **Yes** |

---

## 3. Deterministic Baseline Benchmark (1,000-Cluster Scale)

The deterministic reconciliation engine was evaluated against 1,000 ground-truth clusters with zero access to hidden metadata:

| Metric | Measured Baseline |
| :--- | :--- |
| **Overall Status Accuracy** | **100.00%** (1,000 / 1,000) |
| **Classification Accuracy** | **100.00%** (1,000 / 1,000) |
| **Exception Detection Precision** | **100.00%** |
| **Exception Detection Recall** | **100.00%** |
| **Exception Detection F1 Score** | **1.0000** |
| **False Positives** | **0** |
| **False Negatives** | **0** |
| **Engine Throughput** | **~420–675 records / sec** |

### Scenario Breakdown Accuracy

| Scenario | Records | Status Accuracy | Classification Accuracy |
| :--- | :--- | :--- | :--- |
| `NORMAL_MATCH` | 621 | 100.0% | 100.0% |
| `FEE_MISMATCH` | 70 | 100.0% | 100.0% |
| `MISSING_BANK_TRANSACTION` | 61 | 100.0% | 100.0% |
| `TAX_MISMATCH` | 52 | 100.0% | 100.0% |
| `REFERENCE_ID_DISCREPANCY` | 37 | 100.0% | 100.0% |
| `DUPLICATE_SETTLEMENT` | 37 | 100.0% | 100.0% |
| `MISSING_SETTLEMENT` | 35 | 100.0% | 100.0% |
| `AMOUNT_MISMATCH` | 32 | 100.0% | 100.0% |
| `UNEXPLAINED_EXCEPTION` | 28 | 100.0% | 100.0% |
| `SETTLEMENT_DELAY` | 27 | 100.0% | 100.0% |

---

## 4. Ambiguity Safeguards

When multiple records share similar matching features within the proximity window:
1. The engine **refuses to make an arbitrary probabilistic guess**.
2. It assigns status `REVIEW` and classification `REFERENCE_ID_DISCREPANCY` (or `AMBIGUOUS_COMPETING_MATCHES`).
3. It packages all competing candidates into the `evidence_payload` for human or AI investigation review.

---

## 5. Benchmark Execution Command

```bash
python scripts/run_evaluation.py
```
