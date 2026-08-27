from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.schema import ReconciliationStatus


class ReconciliationEvidencePayload(BaseModel):
    matched_by: List[str] = Field(default_factory=list)
    matching_confidence: float = 100.0
    matching_method: str = "EXACT_REFERENCE"
    calculation: Dict[str, Any] = Field(default_factory=dict)
    evidence_references: Dict[str, Optional[str]] = Field(default_factory=dict)
    signals: List[str] = Field(default_factory=list)
    competing_candidates: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReconciliationItemResponse(BaseModel):
    id: str
    payment_id: str
    order_id: Optional[str] = None
    settlement_id: Optional[str] = None
    bank_transaction_id: Optional[str] = None
    
    order_reference: Optional[str] = None
    payment_reference: Optional[str] = None
    settlement_reference: Optional[str] = None
    bank_reference: Optional[str] = None
    utr_number: Optional[str] = None
    
    expected_settlement_amount: Decimal
    actual_settlement_amount: Optional[Decimal] = None
    expected_bank_amount: Decimal
    actual_bank_amount: Optional[Decimal] = None
    discrepancy_amount: Decimal
    
    matching_score: Decimal
    matching_method: str
    status: ReconciliationStatus
    classification: str
    operational_warning: Optional[str] = None
    
    evidence_payload: Optional[Dict[str, Any]] = None
    reconciled_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReconciliationSummaryResponse(BaseModel):
    total_records: int = 0
    matched_count: int = 0
    exception_count: int = 0
    missing_bank_count: int = 0
    missing_settlement_count: int = 0
    duplicate_count: int = 0
    review_count: int = 0
    
    match_rate_percentage: float = 0.0
    total_expected_amount: Decimal = Decimal("0.00")
    total_actual_amount: Decimal = Decimal("0.00")
    total_discrepancy_amount: Decimal = Decimal("0.00")
    total_explained_by_rules_amount: Decimal = Decimal("0.00")
    total_unresolved_amount: Decimal = Decimal("0.00")
    
    classification_breakdown: Dict[str, int] = Field(default_factory=dict)
    operational_warnings_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ReconciliationRunRequest(BaseModel):
    merchant_id: Optional[str] = None
    proximity_window_days: int = 5
    sla_delay_threshold_days: int = 7
    recalculate_all: bool = True

    model_config = ConfigDict(from_attributes=True)


class ReconciliationRunResult(BaseModel):
    status: str = "success"
    processed_count: int = 0
    duration_ms: float = 0.0
    summary: ReconciliationSummaryResponse

    model_config = ConfigDict(from_attributes=True)
