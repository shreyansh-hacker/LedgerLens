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
| `UNEXPLAINED_EXCEPTION` | ~3% | Financial variance with zero supporting ledger records. | `EXCEPTION` | **No** | **Yes** |

---

## 3. Ground Truth Separation of Concerns

To guarantee an **honest, uncompromised benchmark**:
1. **The Synthetic Engine** creates financial reality and records hidden `GroundTruthMetadata` (`expected_status`, `expected_difference`, `expected_reason`, `is_explainable`).
2. **The Reconciliation Engine** and **AI Investigator** have **zero access** to the ground-truth metadata. They must deduce the truth strictly from the observable database records (`orders`, `payments`, `fees`, `taxes`, `settlements`, `bank_transactions`).
3. **The Evaluation Suite** compares the reconciliation engine's conclusions against the hidden ground truth to compute Precision, Recall, F1, and Hallucination Refusal Rate.

---

## 4. Seeding & CLI Usage

Generate and seed demo data:
```bash
python scripts/seed_demo_data.py --count 1000 --seed 42 --export-dir data/generated
```

Command-line Options:
* `--count`: Total transaction clusters to generate (default: 1000).
* `--seed`: Deterministic PRNG seed (default: 42).
* `--export-dir`: Directory for JSON and CSV file dumps (default: `data/generated`).
* `--skip-db`: Export dataset to files only, skipping database insertion.
