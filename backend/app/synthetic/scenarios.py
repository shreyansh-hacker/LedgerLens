from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ScenarioType(str, Enum):
    NORMAL_MATCH = "NORMAL_MATCH"
    FEE_MISMATCH = "FEE_MISMATCH"
    TAX_MISMATCH = "TAX_MISMATCH"
    MISSING_BANK_TRANSACTION = "MISSING_BANK_TRANSACTION"
    MISSING_SETTLEMENT = "MISSING_SETTLEMENT"
    DUPLICATE_SETTLEMENT = "DUPLICATE_SETTLEMENT"
    REFERENCE_ID_DISCREPANCY = "REFERENCE_ID_DISCREPANCY"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    SETTLEMENT_DELAY = "SETTLEMENT_DELAY"
    UNEXPLAINED_EXCEPTION = "UNEXPLAINED_EXCEPTION"


# Default statistical distribution across scenarios
DEFAULT_SCENARIO_DISTRIBUTION: Dict[ScenarioType, float] = {
    ScenarioType.NORMAL_MATCH: 0.60,
    ScenarioType.FEE_MISMATCH: 0.08,
    ScenarioType.TAX_MISMATCH: 0.05,
    ScenarioType.MISSING_BANK_TRANSACTION: 0.05,
    ScenarioType.MISSING_SETTLEMENT: 0.04,
    ScenarioType.DUPLICATE_SETTLEMENT: 0.04,
    ScenarioType.REFERENCE_ID_DISCREPANCY: 0.04,
    ScenarioType.AMOUNT_MISMATCH: 0.04,
    ScenarioType.SETTLEMENT_DELAY: 0.03,
    ScenarioType.UNEXPLAINED_EXCEPTION: 0.03,
}


class GroundTruthMetadata(BaseModel):
    cluster_id: str
    scenario_type: ScenarioType
    expected_status: str  # "MATCHED", "EXCEPTION", "HUMAN_REVIEW"
    expected_settlement_amount: Decimal
    expected_bank_amount: Decimal
    expected_difference: Decimal
    expected_reason: str
    should_auto_resolve: bool
    should_require_human_review: bool
    is_explainable: bool
    discrepancy_signals: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
