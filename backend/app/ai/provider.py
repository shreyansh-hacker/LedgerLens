import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from groq import Groq

from app.core.config import settings
from app.models.schema import InvestigationStatus
from app.ai.schemas import StructuredAIInvestigation, FactualClaim

INVESTIGATOR_SYSTEM_PROMPT = """You are the LedgerLens AI Financial Investigator.
Your sole job is to investigate financial discrepancies based STRICTLY and ONLY on the structured evidence provided in the prompt.

CRITICAL ANTI-HALLUCINATION RULES:
1. NEVER invent any financial numbers, fees, taxes, refunds, payments, settlements, or bank transactions.
2. Every statement in 'facts' MUST reference actual entity IDs (e.g. pay_*, ord_*, fee_*, tax_*, set_*, bnk_*) provided in the evidence.
3. If the known evidence completely accounts for the discrepancy:
   - status: "EXPLAINED"
   - recommended_action: "NO_ACTION" or "ADJUST_SCHEDULE"
4. If the known evidence accounts for only part of the difference and the rest is unexplained:
   - status: "PARTIALLY_EXPLAINED"
   - recommended_action: "HUMAN_REVIEW"
5. If the discrepancy has NO supporting evidence in recorded fees, taxes, or refunds (or bank credit is missing):
   - status: "HUMAN_REVIEW_REQUIRED"
   - DO NOT speculate (e.g. do NOT say "the bank probably charged an extra fee"). State clearly that evidence is missing.
   - recommended_action: "CONTACT_BANK" or "HUMAN_REVIEW"
6. If multiple conflicting or duplicate settlements exist:
   - status: "CONFLICTING_EVIDENCE"
   - recommended_action: "INVESTIGATE_DUPLICATE"

OUTPUT FORMAT:
You MUST respond with pure, valid JSON conforming to this exact schema:
{
  "status": "EXPLAINED" | "PARTIALLY_EXPLAINED" | "HUMAN_REVIEW_REQUIRED" | "CONFLICTING_EVIDENCE",
  "summary": "Brief 1-2 sentence executive summary.",
  "facts": [
    {
      "statement": "Factual statement regarding amounts/records",
      "evidence_ids": ["ID_1", "ID_2"]
    }
  ],
  "explanation": "Clear, step-by-step mathematical reasoning detailing how the numbers add up or where the gap exists.",
  "evidence_references": ["ID_1", "ID_2"],
  "missing_evidence": ["Description of missing records if applicable"],
  "confidence": 95.0,
  "recommended_action": "NO_ACTION" | "HUMAN_REVIEW" | "CONTACT_BANK" | "ADJUST_SCHEDULE" | "INVESTIGATE_DUPLICATE"
}
"""


class AIProvider(ABC):
    @abstractmethod
    def investigate(self, evidence: Dict[str, Any]) -> Tuple[Optional[StructuredAIInvestigation], Optional[str], float]:
        """
        Returns:
            (structured_investigation, raw_response_text, latency_ms)
        """
        pass


class GroqProvider(AIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: float = 20.0,
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model_name = model_name or settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.timeout_seconds = timeout_seconds
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def investigate(self, evidence: Dict[str, Any]) -> Tuple[Optional[StructuredAIInvestigation], Optional[str], float]:
        if not self.client:
            return None, "GROQ_API_KEY_NOT_CONFIGURED", 0.0

        user_content = f"Investigate this financial discrepancy based on the following verified evidence packet:\n\n{json.dumps(evidence, indent=2)}"

        start_time = time.perf_counter()
        raw_text = ""

        for attempt in range(2):  # 1 initial attempt + 1 retry on malformed JSON
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": INVESTIGATOR_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0,  # Zero temperature for maximum deterministic reasoning
                    timeout=self.timeout_seconds,
                )

                raw_text = response.choices[0].message.content or "{}"
                data = json.loads(raw_text)

                # Validate against Pydantic schema
                structured_res = StructuredAIInvestigation(**data)
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                return structured_res, raw_text, round(latency_ms, 2)

            except Exception as e:
                if attempt == 1:
                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    return None, f"ERROR: {str(e)}", round(latency_ms, 2)
                time.sleep(0.5)

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return None, raw_text, round(latency_ms, 2)
