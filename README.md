# LedgerLens 🔍
> **Every rupee gets an evidence trail.**

LedgerLens is an AI-powered financial reconciliation and investigation platform for merchants. It verifies and matches transactions across orders, payments, payment gateway fees, GST taxes, refunds, settlements, and bank statements, backed by an auditable evidence chain.

---

## ⚡ Core Architecture & Design Philosophy
1. **Deterministic Calculations**: Financial amounts, fees, taxes, and record matching are 100% computed via strict deterministic code using `Decimal` precision.
2. **Machine Learning**: Outlier and anomaly detection via Scikit-Learn's `IsolationForest`.
3. **AI Investigator (Groq API)**: Synthesizes structured evidence, formats human-readable discrepancy breakdowns, cites source facts, and assigns confidence without hallucinating unsupported claims.
4. **Human Review Loop**: Captures uncertain, contradictory, or unexplainable edge cases for merchant review with full audit logging.

---

## 🛠️ Tech Stack
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, Lucide Icons
- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy ORM
- **Database**: PostgreSQL (Supabase) / Local SQLite fallback
- **ML / AI**: Scikit-learn (Isolation Forest), Groq API (`llama-3.3-70b-versatile`)
- **Testing**: Pytest, Vitest / Next.js test runner

---

## 🚀 Quickstart (Local Development)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Generate Synthetic Demo Data
```bash
# From project root:
python scripts/seed_demo_data.py --count 1000 --seed 42
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to view the LedgerLens dashboard.

---

## 📁 Repository Structure
```
ledgerlens/
├── frontend/             # Next.js 14+ UI with Tailwind CSS
├── backend/              # FastAPI application & calculation engines
├── data/
│   ├── synthetic/        # Seed datasets with ground truth labels
│   └── generated/        # Runtime and exported datasets
├── scripts/              # Evaluation benchmarks and seeding scripts
├── docs/                 # System, AI, evaluation, and deployment guides
├── docker-compose.yml    # Local container orchestration
└── README.md
```
