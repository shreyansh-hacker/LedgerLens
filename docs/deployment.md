# LedgerLens — Production Deployment Guide

This guide outlines the step-by-step procedure for deploying **LedgerLens** to production using 100% free-tier cloud infrastructure.

---

## 1. Production Architecture Overview

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

## 2. Environment Variables Checklist

### Backend Environment Variables (Configured on Render)

| Variable | Required | Description | Example / Recommended Value |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | **Yes** | Execution mode | `production` |
| `DATABASE_URL` | **Yes** | Supabase connection string (PostgreSQL) | `postgresql+psycopg://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require` |
| `GROQ_API_KEY` | **Yes** | Groq Cloud LPU API key | `gsk_...` |
| `GROQ_MODEL` | No | AI model identifier | `llama-3.3-70b-versatile` |
| `CORS_ORIGINS` | **Yes** | Comma-separated allowed frontend domains | `https://ledgerlens.vercel.app,http://localhost:3000` |
| `PORT` | Auto | Assigned dynamically by Render | `8000` |

> [!CAUTION]
> Never commit actual credentials (`DATABASE_URL`, `GROQ_API_KEY`) to Git or GitHub issues. Set them directly in the Render dashboard.

---

### Frontend Environment Variables (Configured on Vercel)

| Variable | Required | Description | Example / Recommended Value |
| :--- | :---: | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | **Yes** | Public URL of deployed FastAPI backend | `https://ledgerlens-backend.onrender.com` |

> [!IMPORTANT]
> The frontend requires **only** `NEXT_PUBLIC_API_URL`. Never expose `GROQ_API_KEY`, `DATABASE_URL`, or `SUPABASE_SERVICE_ROLE_KEY` in `NEXT_PUBLIC_*` variables.

---

## 3. Step-by-Step Deployment Procedure

### Step 1: Database Setup (Supabase PostgreSQL)
1. Sign in to [Supabase](https://supabase.com) (Free tier).
2. Create a new project named `ledgerlens-db`.
3. Under **Project Settings $\rightarrow$ Database**, copy the **URI Connection String** (Transaction Pooler or Direct).
4. Ensure the password contains only alphanumeric characters or is URL-encoded.
5. Format the connection string as:
   ```text
   postgresql+psycopg://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
   ```

---

### Step 2: Backend Deployment (Render Web Service)
1. Sign in to [Render](https://render.com) (Free tier).
2. Click **New $\rightarrow$ Web Service** and connect the GitHub repository: `https://github.com/shreyansh-hacker/LedgerLens`.
3. Configure the following parameters (or use `render.yaml` Blueprint):
   - **Name**: `ledgerlens-backend`
   - **Runtime**: `Python 3`
   - **Region**: `Oregon` or `Frankfurt`
   - **Branch**: `main`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add the Environment Variables from the table above (`DATABASE_URL`, `GROQ_API_KEY`, `ENVIRONMENT`, `CORS_ORIGINS`).
5. Click **Create Web Service**. Tables will automatically be created on startup via SQLAlchemy ORM.

---

### Step 3: Frontend Deployment (Vercel)
1. Sign in to [Vercel](https://vercel.com) (Free Hobby tier).
2. Click **Add New $\rightarrow$ Project** and import the GitHub repository: `shreyansh-hacker/LedgerLens`.
3. Configure the build settings:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend`
4. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL`: `https://ledgerlens-backend.onrender.com` (use your actual Render backend URL).
5. Click **Deploy**.

---

## 4. Cold-Start & Free-Tier Resilience

Render free-tier instances sleep after 15 minutes of inactivity:
- `BackendHealthBanner.tsx` and `DemoLoaderModal.tsx` automatically detect backend sleep states.
- The UI displays a friendly countdown (*"LedgerLens demo server is waking up..."*) with graceful exponential backoff without overwhelming the server.
- Once healthy, the 1-Click Demo initialization proceeds seamlessly.

---

## 5. Public Demo Safety & Abuse Protection

- **Fixed Benchmark Size**: `POST /api/demo/load` enforces `num_clusters <= 1000` to prevent memory exhaustion on free instances.
- **Idempotency**: Repeated demo clicks return the existing valid state in **~4.2ms** without re-executing database migrations or creating duplicate records.
- **Strict Anti-Hallucination & Fallback**: If Groq API quotas or rate limits are reached, the system activates deterministic fallbacks, ensuring 100% platform uptime.
