# LedgerLens 🔍
> **Every rupee gets an evidence trail.**

LedgerLens is an AI-powered financial reconciliation and investigation platform built for digital commerce merchants, payment aggregators, and fintech operators. It links and balances transactions across Orders, Payments, Gateway Fees, 18% GST Taxes, Refunds, Settlements, and Nodal Bank Statements—backed by verifiable entity citations and zero-hallucination guardrails.

---

## 🌐 Live Production Deployments

* **Frontend (Vercel)**: [https://ledger-lens-hazel.vercel.app](https://ledger-lens-hazel.vercel.app)
* **Backend (Render)**: [https://ledgerlens-ppzl.onrender.com](https://ledgerlens-ppzl.onrender.com)
* **Health Check**: [https://ledgerlens-ppzl.onrender.com/health](https://ledgerlens-ppzl.onrender.com/health)
* **GitHub Repository**: [https://github.com/shreyansh-hacker/LedgerLens](https://github.com/shreyansh-hacker/LedgerLens)

---

## ⚡ 3-Tier Intelligence Architecture

```text
+---------------------------------------------------------------------------------------+
|                                LedgerLens Architecture                                |
+---------------------------------------------------------------------------------------+
|  Tier 1: Deterministic Engine (Strict Python Decimal)                                 |
|  - Multi-pass reference matching & direct ID linkage                                  |
|  - Penny-exact settlement math, MDR fee schedules, and 18% GST tax deduction          |
|  - 100.0% Status & Classification Accuracy on 1,000-cluster benchmark                 |
|                                                                                       |
|  Tier 2: ML Anomaly Detection Layer (Scikit-Learn Isolation Forest)                   |
|  - Unsupervised population outlier scoring across 14 observable financial features    |
|  - Normalized 0–100 risk scoring with observable feature explanation signals           |
|  - Zero data leakage (strictly zero access to hidden synthetic scenario labels)       |
|                                                                                       |
|  Tier 3: Groq AI Financial Investigator (LLaMA-3.3-70B)                               |
|  - Structured root-cause explanations citing verified ledger entity IDs               |
|  - Strict anti-hallucination rules: escalates missing evidence to Human Review        |
|  - SHA-256 canonical evidence hashing & sub-second LPU inference (0ms cache hits)     |
+---------------------------------------------------------------------------------------+
```

---

## ☁️ Deployment Architecture

```text
                     Web Browser / Client
                               │
                   HTTPS (Vercel Serverless)
                               ▼
              Next.js 14 Frontend Application
                (https://ledger-lens-hazel.vercel.app)
                               │
                  CORS Origin: Vercel Domain
                               ▼
                  FastAPI Python 3.11 Backend
                 (https://ledgerlens-ppzl.onrender.com)
                      ├── Deterministic Multi-Pass Matcher
                      ├── Scikit-Learn Isolation Forest ML
                      └── Natural Language Finance Copilot
                               │                  │
                PgBouncer Transaction Pooler      │ HTTPS (Groq Cloud API)
                               ▼                  ▼
                    Supabase PostgreSQL 15    Groq LPU (LLaMA-3.3-70B)
```

---

## 📊 Ground-Truth Benchmark Results (1,000 Clusters, Seed 42)

| Engine Tier | Metric | Benchmark Result | Performance |
| :--- | :--- | :--- | :--- |
| **Tier 1: Deterministic** | Status Accuracy | **100.00% (1,000 / 1,000)** | ~550 records / sec |
| **Tier 1: Deterministic** | Precision / Recall / F1 | **1.0000 (0 FP / 0 FN)** | Exact Decimal |
| **Tier 2: ML Anomaly** | Outliers Detected | **100 / 1,000 (10.0%)** | 2,228 records / sec |
| **Tier 2: ML Anomaly** | Mean Population Score | **19.98 / 100** | 14 Observable Features |
| **Tier 3: Groq AI** | Fact Grounding Rate | **100.00% (0 Hallucinations)** | ~650 ms inference |
| **Tier 3: Groq AI** | Schema Validity | **100.00% Strict JSON** | 0.0 ms cache hit |

> 📌 **Synthetic Benchmark Disclaimer**: The benchmark dataset comprises 1,000 synthetic transaction clusters across 10 controlled scenarios generated deterministically via Seed 42. It is engineered for testing, auditing, and evaluation. Real merchant data is never exposed.

---

## 🛠️ Production Tech Stack

* **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons
* **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy ORM, Psycopg 3
* **Database**: PostgreSQL (Supabase) via PgBouncer Pooler / Local SQLite
* **Machine Learning**: Scikit-Learn `IsolationForest`
* **AI Acceleration**: Groq Cloud LPU (`llama-3.3-70b-versatile`)
* **Testing & QA**: Pytest (51 automated unit, regression, & security tests)

---

## 🚀 Local Development Quickstart

### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Visit [http://localhost:3000](http://localhost:3000).

### 3. Run Automated Tests
```bash
pytest -v
```

---

## 📁 Repository Structure

```
ledgerlens/
├── frontend/             # Next.js 14 UI (App Router, Tailwind CSS)
│   ├── app/              # Routes: /, /dashboard, /reconciliation, /investigations, /evaluation, /help, /about
│   ├── components/       # Reusable primitives: EvidenceTimeline, CalculationCard, ConfidenceIndicator, CopilotDrawer
│   └── lib/              # Strongly typed API client
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── reconciliation/ # Deterministic multi-pass matching engine
│   │   ├── anomaly/        # Isolation Forest ML feature extractor & detector
│   │   ├── ai/             # Groq AI investigator, evidence assembler, copilot
│   │   ├── synthetic/      # 10 ground-truth scenario generator & seeder
│   │   └── api/            # REST API endpoints (/reconciliation, /anomalies, /investigations, /demo)
│   └── tests/            # 50 comprehensive unit, regression, and security tests
├── docs/                 # System architecture, AI guardrails, demo, evaluation, and deployment guides
└── README.md
```
