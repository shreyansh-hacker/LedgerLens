from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "LedgerLens API"
    version: str = "0.1.0"
    database_connected: bool = True
    ai_service_configured: bool = False
    timestamp: datetime = datetime.utcnow()

    model_config = ConfigDict(from_attributes=True)


class ReconciliationSummary(BaseModel):
    total_records: int = 0
    matched_count: int = 0
    exception_count: int = 0
    human_review_count: int = 0
    resolved_count: int = 0
    match_rate_percentage: float = 0.0
    total_discrepancy_amount: Decimal = Decimal("0.00")
    total_explained_amount: Decimal = Decimal("0.00")
    total_unexplained_amount: Decimal = Decimal("0.00")

    model_config = ConfigDict(from_attributes=True)
