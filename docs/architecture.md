# LedgerLens — Complete System Architecture

> **Every rupee gets an evidence trail.**

LedgerLens is a 3-tier financial intelligence platform combining strict deterministic accounting mathematics, unsupervised ML anomaly detection, and evidence-grounded generative investigation.

---

## 1. End-to-End System Topology

```text
                                 ┌───────────────────────────┐
                                 │      Vercel (Hobby)       │
                                 │  Next.js 14 App Router    │
                                 │ https://ledgerlens.vercel.app│
                                 └─────────────┬─────────────┘
                                               │ HTTPS
                                               ↓
                                 ┌───────────────────────────┐
                                 │     Render (Free Web)     │
                                 │ FastAPI / Python 3.11     │
                                 │ https://api.ledgerlens... │
                                 └──────┬─────────────┬──────┘
                                        │             │
                    ┌───────────────────┘             └───────────────────┐
                    ↓                                                     ↓
        ┌───────────────────────┐                             ┌───────────────────────┐
        │   Supabase (Free DB)  │                             │   Groq Cloud (Free)   │
        │ PostgreSQL (SSL, WAL) │                             │ LLaMA-3.3-70B LPU API │
        └───────────────────────┘                             └───────────────────────┘
```

---

## 2. The 3-Tier Intelligence Architecture

```text
Raw Ledger Records (Orders, Payments, Fees, Taxes, Settlements, Bank Statements)
                                  ↓
+---------------------------------------------------------------------------------------+
|  Tier 1: Deterministic Engine (Strict Python Decimal)                                 |
|  - Multi-Pass Matching: Pass 1 Reference -> Pass 2 Direct ID -> Pass 3 Proximity     |
|  - Penny-exact settlement math, MDR fee schedules, and 18% GST tax deduction          |
|  - 100.0% Status & Classification Accuracy on 1,000-cluster benchmark                 |
+---------------------------------------------------------------------------------------+
                                  ↓
+---------------------------------------------------------------------------------------+
|  Tier 2: ML Anomaly Detection Layer (Scikit-Learn Isolation Forest)                   |
|  - 14 zero-leakage observable features (volumes, fee ratios, settlement delay days)   |
|  - Normalized 0–100 risk scoring with observable feature explanation signals           |
|  - Strictly zero access to hidden synthetic scenario labels                           |
+---------------------------------------------------------------------------------------+
                                  ↓
+---------------------------------------------------------------------------------------+
|  Tier 3: Groq AI Financial Investigator (LLaMA-3.3-70B)                               |
|  - Canonical SHA-256 evidence hashing & 0ms cache retrieval                           |
|  - Structured JSON root-cause explanations citing verified ledger entity IDs          |
|  - Strict anti-hallucination guardrails: missing ledger evidence escalates to Human   |
+---------------------------------------------------------------------------------------+
                                  ↓
+---------------------------------------------------------------------------------------+
|  Human Operator Decision & Immutable Chronological Audit Trail                        |
|  - Reviewer Override, Resolution, and Treasury Escalation with immutable AuditLog     |
+---------------------------------------------------------------------------------------+
```

---

## 3. Multi-Pass Matching Strategy

1. **Pass 1 — Exact Reference Matching**:
   - Matches external identifiers (`payment_reference` $\leftrightarrow$ `settlement_reference`, `settlement.id` $\leftrightarrow$ `bank.settlement_id`, `utr_number`).
   - Confidence: `98–100%`. Method: `EXACT_REFERENCE`.
2. **Pass 2 — Direct ID Linkage**:
   - Matches internal relational keys (`settlement.payment_id == payment.id`).
   - Confidence: `95–100%`. Method: `DIRECT_ID_LINK`.
3. **Pass 3 — Amount + Timestamp Proximity Window (Fallback)**:
   - Evaluates records with corrupted external IDs within a configurable SLA window (`[payment.captured_at, payment.captured_at + 5 days]`).
   - **Ambiguity Safeguard**: If multiple competing candidates share identical amounts within the window, the engine **refuses to guess** and flags `REVIEW` with matching method `AMBIGUOUS_COMPETING_MATCHES`.

---

## 4. Exact Decimal Settlement Arithmetic

$$\text{Expected Net Settlement} = \text{Payment Amount} - \sum(\text{Fees}) - \sum(\text{Taxes}) - \sum(\text{Refunds}) \pm \text{Adjustments}$$

$$\text{Discrepancy Amount} = \text{Expected Net Settlement} - \text{Actual Bank Credit}$$

All monetary computations use Python `Decimal` and PostgreSQL `NUMERIC(14, 2)`. Floating point representation is strictly prohibited.

---

## 5. Composite System Confidence Model

The system calculates a multi-factor confidence metric rather than relying on LLM self-reporting:

$$\text{System Confidence} = 0.35 \cdot C_{\text{calc}} + 0.25 \cdot C_{\text{compl}} + 0.20 \cdot C_{\text{match}} + 0.20 \cdot C_{\text{ai}} - P_{\text{anom}}$$

- $C_{\text{calc}}$: Deterministic calculation agreement ($100\%$ if arithmetic balances, $0\%$ if unverified variance).
- $C_{\text{compl}}$: Evidence completeness ($100\%$ if payment, settlement, and bank credit are all present).
- $C_{\text{match}}$: Match quality score ($95–100\%$ for Pass 1 / Pass 2).
- $C_{\text{ai}}$: AI factual grounding ($100\%$ when every claim cites verified entity IDs).
- $P_{\text{anom}}$: Anomaly penalty ($0.05 \cdot \text{Normalized Anomaly Score}$).
