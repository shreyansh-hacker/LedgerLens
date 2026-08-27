# LedgerLens AI & ML Architecture

## 1. Multi-Tiered Intelligence Architecture

LedgerLens enforces strict separation between deterministic financial logic, unsupervised population anomaly modeling, and generative reasoning:

```
+-------------------------------------------------------------------------+
|                  Deterministic Reconciliation Engine                    |
|  - Exact Decimal arithmetic (money calculations, fees, GST taxes)      |
|  - Multi-pass ID & Reference Matching                                  |
|  - Ground-truth rule verification                                       |
+-------------------------------------------------------------------------+
                                     ↓
+-------------------------------------------------------------------------+
|                     ML Anomaly Detection Layer                          |
|  - Scikit-Learn Isolation Forest (unsupervised outlier scoring)         |
|  - Continuous normalized anomaly score (0–100) and Severity Tiers        |
|  - Observable feature deviations (amounts, fee ratios, latency)        |
+-------------------------------------------------------------------------+
                                     ↓
+-------------------------------------------------------------------------+
|                      Groq AI Investigator (Phase 5)                     |
|  - LLM receives ONLY structured verified facts & anomaly features       |
|  - Strict JSON schema generation with hallucination guardrails          |
|  - Natural language explanations citing verified evidence               |
+-------------------------------------------------------------------------+
```

---

## 2. Why Machine Learning (Isolation Forest)?

* **Deterministic Engine** answers: *"Can we mathematically account for this discrepancy using ledger records?"*
* **ML Anomaly Detector** answers: *"Is this transaction pattern unusual compared to the broader merchant baseline?"*

A transaction can be:
* `MATCHED + LOW ANOMALY`: Standard ₹500 grocery order settled in 24 hours.
* `MATCHED + HIGH ANOMALY`: ₹120,000 enterprise transaction settled with a 25-day delay (amounts reconcile, but volume and latency are extreme population outliers).
* `EXCEPTION + HIGH ANOMALY`: ₹50,000 payment with missing settlement batch and zero bank credit.

### Important Distinction: Anomaly vs Fraud
The ML layer is an **unsupervised statistical outlier detector, NOT a fraud classifier**. An anomaly indicates statistical irregularity within the merchant's distribution, prompting investigation rather than making unverified fraud allegations.

---

## 3. Observable Features (Zero Data Leakage)

The feature matrix is extracted strictly from observable database records:
1. `payment_amount`: Monetary value in INR.
2. `amount_ratio_to_merchant_median`: Ratio of transaction amount to merchant baseline median.
3. `fee_to_amount_ratio`: Ratio of gateway MDR fee to total payment.
4. `tax_to_fee_ratio`: Ratio of tax deducted to gateway fee (expected: ~0.18).
5. `discrepancy_to_amount_ratio`: Relative magnitude of discrepancy to total transaction.
6. `settlement_delay_hours`: Latency between payment capture and settlement time.
7. `bank_delay_hours`: Latency between settlement batch and bank credit.
8. `hour_of_day`: Temporal capture distribution (0–23).
9. `day_of_week`: Day of week (0–6).
10. `is_settlement_missing`: Binary flag (1.0 if settlement is null).
11. `is_bank_missing`: Binary flag (1.0 if bank transaction is null).
12. `is_duplicate`: Binary flag (1.0 if multiple settlements exist).
13. `matching_confidence`: Multi-pass matcher score (0–100).
14. `has_operational_warning`: Binary indicator for SLA delays.

*Leakage Prevention*: The feature extractor never accesses, imports, or computes values from `GroundTruthMetadata` or `scenario_type`.

---

## 4. Normalization & Severity Thresholds

Isolation Forest decision function scores ($s \in [-0.75, -0.35]$) are normalized to a standard `0–100` scale:

$$\text{Normalized Score} = \left( \frac{\max(s) - s}{\max(s) - \min(s)} \right) \times 100$$

* **LOW Anomaly**: $0.0 \le \text{Score} < 40.0$
* **MEDIUM Anomaly**: $40.0 \le \text{Score} < 70.0$
* **HIGH Anomaly**: $70.0 \le \text{Score} \le 100.0$
