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
|  - Strict JSON schema generation with anti-hallucination guardrails     |
|  - Natural language explanations citing verified evidence               |
|  - SHA-256 canonical evidence caching & multi-factor confidence scoring |
+-------------------------------------------------------------------------+
```

---

## 2. Groq AI Financial Investigator

### Evidence-First Architecture
The AI Investigator answers:
> *"Why did this financial discrepancy happen, based strictly on available evidence?"*

The backend sanitizes and packages verified entity records into a canonical JSON payload:
- **Payment & Order references**
- **Recorded Fees, GST Taxes, and Refunds**
- **Settlement Net & Gross calculations**
- **Bank statement credit and UTR numbers**
- **ML Anomaly score & feature signals**

### Strict Anti-Hallucination Guardrails
1. **Never Invent Data**: The LLM is strictly prohibited from inventing financial figures, fees, taxes, refunds, or transaction IDs.
2. **Traceable Fact Grounding**: Every fact claimed in `facts` must reference explicit IDs (e.g. `pay_*`, `fee_*`, `tax_*`, `set_*`, `bnk_*`).
3. **Escalation on Gaps**: If evidence is missing or unexplained, the AI classifies the record as `HUMAN_REVIEW_REQUIRED` and articulates the missing evidence rather than guessing.
4. **Conflicting Evidence**: If duplicate settlement records exist, the AI tags `CONFLICTING_EVIDENCE` and recommends `INVESTIGATE_DUPLICATE`.

---

## 3. System-Level Composite Confidence Scoring

System confidence does not blindly trust model self-evaluations. It is computed as a multi-factor composite:

$$\text{System Confidence} = 0.35 \times \text{Calc Agreement} + 0.25 \times \text{Evidence Completeness} + 0.20 \times \text{Matching Score} + 0.20 \times \text{AI Grounding} - \text{Anomaly Penalty}$$

* **HIGH Tier**: $\ge 88.0\%$
* **MEDIUM Tier**: $60.0\% \le \text{Score} < 88.0\%$
* **LOW Tier**: $< 60.0\%$

---

## 4. SHA-256 Canonical Evidence Caching & Deterministic Fallback

* **Evidence Hashing**: Every evidence payload is canonicalized (sorted keys, compact delimiters) and hashed using SHA-256 (`evidence_hash`). Subsequent requests for identical financial states return instantaneous cached results ($0\text{ ms}$).
* **Provider Fallback**: If Groq encounters network outages, rate limits, or validation errors (after 1 controlled retry), the system provides an immediate deterministic fallback without service degradation.

---

## 5. Natural Language Finance Copilot

The assistant endpoint (`POST /api/assistant/query`) maps human-language questions to safe, predefined backend query tools (zero raw LLM SQL execution):
* `get_reconciliation_summary()`
* `get_largest_discrepancies()`
* `get_delayed_settlements()`
* `get_entity_detail()`
