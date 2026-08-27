from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.schema import AnomalySeverity, ReconciliationStatus


class AnomalyItemResponse(BaseModel):
    id: str
    reconciliation_id: str
    payment_id: str
    order_reference: Optional[str] = None
    payment_reference: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    
    payment_amount: Decimal
    discrepancy_amount: Decimal
    reconciliation_status: ReconciliationStatus
    reconciliation_classification: str
    
    raw_anomaly_score: float
    normalized_score: float
    severity: AnomalySeverity
    is_anomaly: bool
    
    detected_features: Dict[str, Any] = Field(default_factory=dict)
    explanation_signals: List[str] = Field(default_factory=list)
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnomalySummaryResponse(BaseModel):
    total_evaluated: int = 0
    anomalies_detected: int = 0
    anomaly_rate_percentage: float = 0.0
    
    severity_breakdown: Dict[str, int] = Field(default_factory=dict)
    avg_normalized_score: float = 0.0
    top_detected_signals: Dict[str, int] = Field(default_factory=dict)
    model_version: str = "isolation_forest_v1.0"

    model_config = ConfigDict(from_attributes=True)


class AnomalyRunRequest(BaseModel):
    contamination: float = 0.10
    n_estimators: int = 100
    random_state: int = 42
    high_severity_threshold: float = 70.0
    medium_severity_threshold: float = 40.0

    model_config = ConfigDict(from_attributes=True)


class AnomalyRunResult(BaseModel):
    status: str = "success"
    processed_count: int = 0
    anomalies_found: int = 0
    duration_ms: float = 0.0
    summary: AnomalySummaryResponse

    model_config = ConfigDict(from_attributes=True)
