# LedgerLens Architecture

## 1. System Overview
LedgerLens is an AI-powered financial reconciliation and investigation platform built to provide an irrefutable evidence trail for every rupee.

```
Orders + Payments + Fees + Taxes + Refunds + Settlements + Bank Records
                                 ↓
                 Deterministic Data Validation
                                 ↓
         Multi-Pass Matching Engine (Pass 1 → Pass 2 → Pass 3)
                                 ↓
       Exact Precision Financial Arithmetic (Decimal / NUMERIC)
                                 ↓
       Rule-Based Exception Classifier & Missing/Duplicate Detector
                                 ↓
      Machine-Readable Structured Evidence Trail & Audit Logging
                                 ↓
                  Reconciliation Results Schema
```

---

## 2. Multi-Pass Matching Strategy

1. **Pass 1 — Exact Reference Matching**:
   * Direct match on external references (`payment_reference` <-> `settlement_reference`, `settlement.id` <-> `bank.settlement_id`, `utr_number`).
   * Confidence: `98–100%`. Method: `EXACT_REFERENCE`.
2. **Pass 2 — Direct ID Linkage**:
   * Standard relational foreign keys (`settlement.payment_id == payment.id`).
   * Confidence: `95–100%`. Method: `DIRECT_ID_LINK`.
3. **Pass 3 — Amount + Timestamp Proximity Window (Fallback)**:
   * Used when identifiers are corrupted or non-standard. Searches within configured merchant scope and time window (`[payment.captured_at, payment.captured_at + 5 days]`).
   * **Ambiguity Safeguard**: If multiple competing candidates share identical amounts within the window, the engine **refuses to pick arbitrarily** and flags the record as `REVIEW` with matching method `AMBIGUOUS_COMPETING_MATCHES`.

---

## 3. Financial Calculation Engine

$$\text{Expected Net Settlement} = \text{Payment Amount} - \sum(\text{Fees}) - \sum(\text{Taxes}) - \sum(\text{Refunds}) \pm \text{Adjustments}$$

$$\text{Discrepancy Amount} = \text{Expected Net Settlement} - \text{Actual Bank Credit}$$

All figures use `Decimal` with 2 decimal places (`Numeric(14, 2)`). Floating point arithmetic is strictly prohibited.

---

## 4. Reconciliation Status & Taxonomy

* **Statuses**: `MATCHED`, `EXCEPTION`, `MISSING_SETTLEMENT`, `MISSING_BANK_TRANSACTION`, `DUPLICATE`, `REVIEW`.
* **Classifications**: `NONE`, `FEE_MISMATCH`, `TAX_MISMATCH`, `MISSING_BANK_TRANSACTION`, `MISSING_SETTLEMENT`, `DUPLICATE_SETTLEMENT`, `REFERENCE_ID_DISCREPANCY`, `AMOUNT_MISMATCH`, `SETTLEMENT_DELAY`, `UNEXPLAINED_EXCEPTION`.
* **Operational Warnings**: e.g., `SETTLEMENT_DELAY` tracks SLA latency breaches while keeping financially accurate settlements categorized as `MATCHED`.
