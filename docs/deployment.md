# LedgerLens Deployment Guide

## Target Free-Tier Stack
- **Frontend**: Vercel Free Tier (Next.js 14+)
- **Backend**: Render Free Web Service (FastAPI)
- **Database**: Supabase Free PostgreSQL
- **AI**: Groq Free Tier API

## Cold Start Tolerance
The frontend includes an interactive wake-up state checking `/api/health` with automatic reconnection while Render spins up from sleep.
