from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.schemas.common import HealthResponse
from datetime import datetime
import os

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    ai_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())

    return HealthResponse(
        status="ok" if db_connected else "degraded",
        service="LedgerLens API",
        version=settings.VERSION,
        database_connected=db_connected,
        ai_service_configured=ai_configured,
        timestamp=datetime.utcnow()
    )
