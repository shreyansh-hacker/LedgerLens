# LedgerLens — Production Demo Mode & Judge Walkthrough

This document describes the design, architecture, and operational lifecycle of the **LedgerLens Demo Mode**, specifically tailored for hackathon judges, operators, and evaluators.

---

## 1. 3-Minute Judge Walkthrough Script

| Timestamp | Screen / Action | What the Judge Sees & Learns |
| :--- | :--- | :--- |
| **0:00 — Problem** | Landing Page (`/`) | **Problem**: In high-volume e-commerce, payment reconciliation is fragmented across gateway webhooks, settlement batches, and nodal bank statements. Unannounced fee tier changes, missing 18% GST deductions, and missing bank credits create massive financial leaks. |
| **0:20 — Live Demo** | Click `[Try Live Demo]` | **Zero-Setup Demo**: The system instantly generates synthetic transaction clusters spanning 10 controlled scenarios, seeds the database, executes 3-pass reconciliation, fits Isolation Forest ML, and preloads AI investigations. |
| **0:45 — Dashboard** | Dashboard (`/dashboard`) | **Real-Time KPIs**: Records processed, 70.0% clean match rate, total discrepancy amounts, and ML anomaly severity profiles—grounded in real database calculations. |
| **1:10 — Discrepancy** | "Start Exploring" Banner | Click `[Inspect Evidence Trail]` on the recommended featured discrepancy (e.g. `rec_00006`). |
| **1:30 — Evidence Trail** | Investigation Workspace | **Verifiable Evidence Chain**: Side-by-side settlement math card showing Customer Gross Payment minus Gateway Fee minus 18% GST equals Expected Settlement, contrasted against Actual Bank Credit. |
| **1:50 — ML Anomaly** | ML Risk Card | **Zero-Leakage ML**: Scikit-Learn Isolation Forest scores the transaction across 14 observable features (e.g. fee ratio surges, latency), flagging population outliers without seeing synthetic labels. |
| **2:10 — AI Investigator** | AI Investigation Report | **Evidence-Grounded AI**: Groq LLaMA-3.3-70B explains root cause citing explicit entity IDs (`pay_*`, `fee_*`, `set_*`). Zero hallucination: if ledger evidence is missing, it refuses to guess and calls out missing records. |
| **2:30 — Human Review** | Review Panel & Audit Trail | **Human Decision & Compliance**: Operator inputs a review note, marks as `RESOLVED` or `ESCALATE`, appending an immutable audit trail entry. |
| **2:45 — Evaluation** | Benchmark (`/evaluation`) | **Ground-Truth Matrix**: Independent verification matrix proving 100.0% deterministic status accuracy across all 10 scenarios and sub-second inference speeds. |
| **3:00 — Why LedgerLens** | Navbar / About (`/about`) | **The Winning Difference**: Deterministic exact math for rupees + Unsupervised ML for population anomalies + Grounded AI for root-cause explanations + Complete Human Control. |

---

## 2. Demo Architecture & Intelligence Pipeline

```text
+-------------------------------------------------------------------------+
|                        LedgerLens Demo Pipeline                         |
+-------------------------------------------------------------------------+
| 1. Synthetic Generator (Seed: 42)                                       |
|    - 1,000 transaction clusters spanning 10 controlled scenarios         |
|                                                                         |
| 2. Database Seeder (SQLAlchemy ORM)                                     |
|    - Clean relational insertion across 8 tables with cascade safety     |
|                                                                         |
| 3. Deterministic Reconciliation Engine (Python Decimal)                 |
|    - Pass 1: Strict Exact Reference Matching                            |
|    - Pass 2: Direct ID Entity Linkage                                   |
|    - Pass 3: Proximity & Ambiguity Resolution                           |
|                                                                         |
| 4. ML Anomaly Detection (Scikit-Learn Isolation Forest)                 |
|    - 14 zero-leakage observable features                                |
|    - 0–100 normalized population outlier scores                         |
|                                                                         |
| 5. Groq AI Financial Investigator (LLaMA-3.3-70B)                       |
|    - SHA-256 Canonical Evidence Hashing & Caching                       |
|    - Strict anti-hallucination fact citation                            |
|    - Composite multi-factor system confidence scoring                   |
+-------------------------------------------------------------------------+
```

---

## 3. Demo State Machine

The frontend interactive modal (`DemoLoaderModal.tsx`) transitions through explicit lifecycle states:

| State | Action / Backend Call | User Interface Feedback |
| :--- | :--- | :--- |
| `IDLE` | Modal closed or initial trigger | Button ready |
| `WAKING_BACKEND` | `GET /health` with backoff | Friendly Render spin-up timer if cold |
| `CHECKING_STATUS` | `GET /api/demo/status` | Verifies active dataset readiness |
| `GENERATING_DATA` | Synthetic engine initialized | Animated step checkmark |
| `SEEDING_DATABASE` | Relational table insertion | Animated step checkmark |
| `RECONCILING` | Multi-pass matching pipeline | Animated step checkmark |
| `ANALYZING_ANOMALIES`| Isolation Forest fit & score | Animated step checkmark |
| `PREPARING_INVESTIGATIONS` | Pre-computes sample AI reports | Animated step checkmark |
| `READY` | Completed with summary KPIs | Instant `[Explore Dashboard]` button |
| `ERROR` | API or network exception caught | Plain English error + `[Retry]` |

---

## 4. Idempotency & Safety Guarantees

- **Zero Duplication**: Calling `POST /api/demo/load` multiple times checks table counts before generation. If the 1,000-cluster dataset already exists, the server returns the cached summary in **~4ms** without inserting duplicate records or modifying balances.
- **Force Reset**: Passing `force_reset=True` triggers `DatabaseSeeder.reset_database()` to cleanly purge child and parent records before re-seeding.
- **Zero Synthetic Ground-Truth Leakage**: The reconciliation engine, ML anomaly detector, and AI investigator operate solely on observable financial data.

---

## 5. Cold-Start & Free-Tier Resilience

- **Render Sleep Awareness**: When backend instances sleep on free tiers, `BackendHealthBanner` and `DemoLoaderModal` detect connectivity without hammering endpoints.
- **AI Fallback**: If Groq API keys are absent, rate-limited, or encountering network issues, LedgerLens automatically activates deterministic fallbacks, displaying structured mathematical variance explanations and recommending human operator review.

---

## 6. Curated Guided Walkthrough Cases

The endpoint `GET /api/demo/featured` dynamically discovers representative cases in the database for the judge to inspect:

1. **Gateway Fee Mismatch**: Demonstrates exact arithmetic breakdown when gateway deductions diverge from agreed merchant MDR schedules.
2. **Missing Bank Credit**: Demonstrates ledger verification when a gateway settlement is finalized but bank statement credit is absent.
3. **Unexplained Variance / Missing Evidence**: Demonstrates AI anti-hallucination guardrails refusing to invent unrecorded bank deductions and escalating to `HUMAN_REVIEW_REQUIRED`.
