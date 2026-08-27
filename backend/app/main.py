from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router
from app.api.health import router as health_router
import app.models  # Ensure all models are imported before create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LedgerLens — AI-Powered Financial Reconciliation & Investigation Platform",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount direct /health for root health checkers (Render, AWS, etc.)
app.include_router(health_router, prefix="", tags=["Health"])

# Mount API router under /api
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "service": "LedgerLens Financial Reconciliation Engine",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
        "message": "Every rupee gets an evidence trail."
    }
