from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.schema import InvestigationStatus, ReconciliationStatus, AnomalySeverity


class FactualClaim(BaseModel):
    statement: str
    evidence_ids: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class StructuredAIInvestigation(BaseModel):
    status: InvestigationStatus
    summary: str
    facts: List[FactualClaim] = Field(default_factory=list)
    explanation: str
    evidence_references: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=100.0)
    recommended_action: str

    model_config = ConfigDict(from_attributes=True)


class InvestigationItemResponse(BaseModel):
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
    
    investigation_status: InvestigationStatus
    summary: str
    facts: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str
    evidence_references: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    
    ai_confidence: float
    system_confidence: float
    confidence_tier: str
    
    recommended_action: str
    human_override: bool = False
    reviewer_note: Optional[str] = None
    cached: bool = False
    latency_ms: float = 0.0
    model_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationSummaryResponse(BaseModel):
    total_investigations: int = 0
    explained_count: int = 0
    partially_explained_count: int = 0
    human_review_count: int = 0
    conflicting_evidence_count: int = 0
    avg_system_confidence: float = 0.0
    cached_rate_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class AssistantQueryRequest(BaseModel):
    query: str
    merchant_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssistantQueryResponse(BaseModel):
    query: str
    answer: str
    intent: str
    retrieved_data_summary: Dict[str, Any] = Field(default_factory=dict)
    evidence_sources: List[str] = Field(default_factory=list)
    confidence: float = 95.0

    model_config = ConfigDict(from_attributes=True)
