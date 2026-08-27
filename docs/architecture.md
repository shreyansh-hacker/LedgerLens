# LedgerLens Architecture

## Overview
LedgerLens is an AI-powered financial reconciliation and investigation platform built to provide an irrefutable evidence trail for every rupee.

## System Architecture
1. **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide icons.
2. **Backend**: FastAPI (Python 3.11), Pydantic v2 validation.
3. **Database Layer**: SQLAlchemy ORM with support for PostgreSQL (Supabase) and local SQLite fallback, using `Decimal` / `NUMERIC` for precise financial math.
4. **Reconciliation Engine**: Deterministic multi-signal matching (ID, amount, timestamp, fees, taxes).
5. **Anomaly Detection**: Scikit-Learn Isolation Forest.
6. **AI Investigator**: Groq API (`llama-3.3-70b-versatile`) with structured JSON validation and strict hallucination guardrails.
7. **Cold Start Resilience**: Graceful `/api/health` polling for free-tier deployments.

*(Detailed architectural documentation will be expanded across phases)*
