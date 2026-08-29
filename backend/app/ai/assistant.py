import json
import re
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.schema import (
    ReconciliationResult,
    InvestigationResult,
    Payment,
    Order,
    Settlement,
    BankTransaction,
)
from app.reconciliation.engine import DeterministicReconciliationEngine
from app.ai.schemas import AssistantQueryResponse
from groq import Groq


ASSISTANT_SYSTEM_PROMPT = """You are the LedgerLens AI Finance Copilot.
You assist financial controllers, CFOs, and operations managers by answering questions about reconciliation, anomalies, and settlements.

CRITICAL RULES:
1. Ground your response STRICTLY and ONLY in the provided retrieved data context.
2. If the user asks for specific transactions, cite the exact references (e.g. pay_*, ord_*, set_*, bnk_*).
3. If data is not found, state clearly that no matching records were found in the database.
4. Format your response cleanly with markdown bullet points and INR (₹) amounts.
"""


class FinanceAssistant:
    """
    Natural Language Finance Copilot.
    Maps natural language queries to predefined, safe backend retrieval tools (Zero raw SQL).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def query(self, user_query: str, db: Session, merchant_id: Optional[str] = None) -> AssistantQueryResponse:
        intent, retrieved_data, sources = self._route_and_retrieve(user_query=user_query, db=db, merchant_id=merchant_id)

        if not self.client:
            # Deterministic fallback response if Groq is not configured
            return AssistantQueryResponse(
                query=user_query,
                answer=f"**Retrieved Context**: Found {len(retrieved_data)} relevant data points for your query. (AI summary unavailable without API key).",
                intent=intent,
                retrieved_data_summary=retrieved_data,
                evidence_sources=sources,
                confidence=90.0,
            )

        prompt_context = f"User Question: {user_query}\n\nRetrieved Database Facts:\n{json.dumps(retrieved_data, indent=2, default=str)}"

        candidate_models = [settings.GROQ_MODEL or "qwen/qwen3.8-27b"]
        if "qwen/qwen3.8-27b" not in candidate_models:
            candidate_models.append("qwen/qwen3.8-27b")

        answer = ""
        for model in candidate_models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": ASSISTANT_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_context},
                    ],
                    temperature=0.1,
                    max_tokens=600,
                )
                answer = response.choices[0].message.content or "No response generated."
                break
            except Exception as e:
                err_msg = str(e)
                if "model_not_found" in err_msg or "404" in err_msg:
                    continue
                answer = f"Found relevant reconciliation records, but LLM summarization encountered an issue ({err_msg})."
                break

        if not answer:
            answer = f"**Retrieved Context**: Found {len(retrieved_data)} data points for your query."

        return AssistantQueryResponse(
            query=user_query,
            answer=answer,
            intent=intent,
            retrieved_data_summary=retrieved_data,
            evidence_sources=sources,
            confidence=95.0,
        )

    def _route_and_retrieve(
        self,
        user_query: str,
        db: Session,
        merchant_id: Optional[str] = None
    ) -> tuple[str, Dict[str, Any], List[str]]:
        """
        Extracts intent from query and runs strict deterministic DB lookup.
        Prevents LLM from writing arbitrary SQL.
        """
        q_lower = user_query.lower()
        sources = []

        # 1. Look for specific payment / transaction IDs (e.g., pay_00006)
        id_match = re.search(r"(pay_[a-zA-Z0-9_-]+|ord_[a-zA-Z0-9_-]+|set_[a-zA-Z0-9_-]+|rec_[a-zA-Z0-9_-]+)", user_query)
        if id_match:
            entity_ref = id_match.group(1)
            rec = None
            if entity_ref.startswith("pay_"):
                rec = db.query(ReconciliationResult).filter(ReconciliationResult.payment_id == entity_ref).first()
            elif entity_ref.startswith("rec_"):
                rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == entity_ref).first()
            elif entity_ref.startswith("set_"):
                rec = db.query(ReconciliationResult).filter(ReconciliationResult.settlement_id == entity_ref).first()

            if rec:
                sources.append(rec.payment_id)
                inv = db.query(InvestigationResult).filter(InvestigationResult.reconciliation_id == rec.id).first()
                return (
                    "GET_ENTITY_DETAIL",
                    {
                        "reconciliation_id": rec.id,
                        "payment_id": rec.payment_id,
                        "status": rec.status.value if hasattr(rec.status, "value") else str(rec.status),
                        "classification": rec.classification,
                        "expected_settlement": f"₹{rec.expected_settlement_amount}",
                        "actual_bank_credit": f"₹{rec.actual_bank_amount}" if rec.actual_bank_amount else "Missing",
                        "discrepancy_amount": f"₹{rec.discrepancy_amount}",
                        "ai_summary": inv.summary if inv else "No preloaded AI investigation",
                        "recommended_action": inv.recommended_action if inv else "Inspect Evidence",
                    },
                    sources
                )

        # 2. Delayed Settlements Query
        if any(w in q_lower for w in ["delayed", "delay", "late", "sla"]):
            delayed_recs = db.query(ReconciliationResult).filter(
                ReconciliationResult.operational_warning.isnot(None)
            ).limit(5).all()
            delayed_list = [{"reconciliation_id": r.id, "payment_id": r.payment_id, "warning": r.operational_warning} for r in delayed_recs]
            return (
                "GET_DELAYED_SETTLEMENTS",
                {
                    "delayed_count": len(delayed_list),
                    "delayed_settlements": delayed_list,
                },
                [r.payment_id for r in delayed_recs]
            )

        # 3. Aggregated Unresolved / Exceptions Query
        if any(w in q_lower for w in ["unresolved", "exception", "discrepancy", "unreconciled", "missing", "difference"]):
            summary = DeterministicReconciliationEngine.compute_summary(db=db, merchant_id=merchant_id)
            unresolved_recs = db.query(ReconciliationResult).filter(
                ReconciliationResult.status != "MATCHED"
            ).limit(5).all()

            sample_list = []
            for r in unresolved_recs:
                sample_list.append({
                    "reconciliation_id": r.id,
                    "payment_id": r.payment_id,
                    "discrepancy": f"₹{r.discrepancy_amount}",
                    "classification": r.classification
                })
                sources.append(r.payment_id)

            return (
                "GET_OVERVIEW_WITH_EXCEPTIONS",
                {
                    "total_records": summary.total_records,
                    "match_rate": f"{summary.match_rate_percentage}%",
                    "total_discrepancy": f"₹{summary.total_discrepancy_amount}",
                    "total_unresolved": f"₹{summary.total_unresolved_amount}",
                    "sample_exceptions": sample_list,
                },
                sources
            )

        # 3. Default Summary Query
        summary = DeterministicReconciliationEngine.compute_summary(db=db, merchant_id=merchant_id)
        return (
            "GET_RECONCILIATION_SUMMARY",
            {
                "total_records": summary.total_records,
                "matched_count": summary.matched_count,
                "exception_count": summary.exception_count,
                "match_rate": f"{summary.match_rate_percentage}%",
                "total_expected": f"₹{summary.total_expected_amount}",
                "total_actual": f"₹{summary.total_actual_amount}",
            },
            sources
        )
