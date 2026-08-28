# LedgerLens — Production Demo Mode & Judge Walkthrough

This document describes the design, architecture, and operational lifecycle of the **LedgerLens Demo Mode**, specifically tailored for hackathon judges, operators, and evaluators.

---

## 1. Primary Demo Experience (2–3 Minutes)

A judge can evaluate the complete system without installing dependencies, running terminal commands, preparing CSVs, or configuring API credentials:

```text
Landing Page (/)
      ↓
Click [Try Live Demo]
      ↓
Modal: Backend wake-up & real-time stage progress
      ↓
1,000 Synthetic Transactions Generated (Seed: 42)
      ↓
Multi-Pass Deterministic Reconciliation Executed
      ↓
Isolation Forest Anomaly Scoring Fitted
      ↓
Groq AI Investigator Pre-generates Grounded Explanations
      ↓
Dashboard Opens with Live KPIs & "Start Exploring" Featured Case
      ↓
Judge Clicks [Inspect Evidence Trail] to view Hero Workspace
```

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
