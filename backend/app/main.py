import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router
from app.api.health import router as health_router
import app.models  # Ensure all models are imported before create_all

logger = logging.getLogger("ledgerlens")


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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Production-safe global exception handler:
    Logs error internally but never leaks stack traces or credentials to clients.
    """
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred while processing the financial request. Deterministic records remain intact."},
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
