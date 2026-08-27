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

        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": ASSISTANT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_context},
                ],
                temperature=0.1,
                max_tokens=600,
            )
            answer = response.choices[0].message.content or "No response generated."
        except Exception as e:
            answer = f"Found relevant reconciliation records, but LLM summarization encountered an issue ({str(e)})."

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
        q = user_query.lower()

        # Check for specific ID search: pay_*, ord_*, rec_*, inv_*, set_*
        id_match = re.search(r"\b(pay_\w+|ord_\w+|rec_\w+|inv_\w+|set_\w+|bnk_\w+|clu_\w+)\b", q)
        if id_match:
            entity_id = id_match.group(1)
            return self._tool_get_entity_detail(entity_id=entity_id, db=db)

        # Intent 1: Delayed settlements
        if "delay" in q or "latency" in q or "sla" in q:
            return self._tool_get_delayed_settlements(db=db, limit=5)

        # Intent 2: Unresolved or Largest Discrepancies
        if "largest" in q or "biggest" in q or "top" in q or "unexplained" in q:
            return self._tool_get_largest_discrepancies(db=db, limit=5)

        # Intent 3: High level summary / unresolved amount
        if "summary" in q or "unresolved" in q or "how much" in q or "overview" in q or "total" in q:
            return self._tool_get_summary(db=db, merchant_id=merchant_id)

        # Default fallback tool: get summary + top exceptions
        return self._tool_get_summary_with_exceptions(db=db, merchant_id=merchant_id)

    def _tool_get_summary(self, db: Session, merchant_id: Optional[str]) -> tuple[str, Dict[str, Any], List[str]]:
        sum_data = DeterministicReconciliationEngine.compute_summary(db, merchant_id=merchant_id)
        data = {
            "total_records": sum_data.total_records,
            "match_rate": f"{sum_data.match_rate_percentage}%",
            "total_discrepancy": f"₹{sum_data.total_discrepancy_amount:,.2f}",
            "total_unresolved": f"₹{sum_data.total_unresolved_amount:,.2f}",
            "exceptions_count": sum_data.exception_count,
            "missing_bank_count": sum_data.missing_bank_count,
            "missing_settlement_count": sum_data.missing_settlement_count,
            "operational_warnings": sum_data.operational_warnings_count,
        }
        return "GET_RECONCILIATION_SUMMARY", data, ["reconciliation_results"]

    def _tool_get_largest_discrepancies(self, db: Session, limit: int = 5) -> tuple[str, Dict[str, Any], List[str]]:
        results = db.query(ReconciliationResult).filter(
            ReconciliationResult.discrepancy_amount != Decimal("0.00")
        ).order_by(ReconciliationResult.discrepancy_amount.desc()).limit(limit).all()

        items = []
        sources = []
        for r in results:
            items.append({
                "reconciliation_id": r.id,
                "payment_id": r.payment_id,
                "discrepancy": f"₹{r.discrepancy_amount:,.2f}",
                "classification": r.classification,
                "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            })
            sources.append(r.payment_id)

        return "GET_LARGEST_DISCREPANCIES", {"top_discrepancies": items}, sources

    def _tool_get_delayed_settlements(self, db: Session, limit: int = 5) -> tuple[str, Dict[str, Any], List[str]]:
        results = db.query(ReconciliationResult).filter(
            ReconciliationResult.operational_warning == "SETTLEMENT_DELAY"
        ).limit(limit).all()

        items = []
        sources = []
        for r in results:
            items.append({
                "reconciliation_id": r.id,
                "payment_id": r.payment_id,
                "settlement_id": r.settlement_id,
                "expected_settlement": f"₹{r.expected_settlement_amount:,.2f}",
                "actual_settlement": f"₹{r.actual_settlement_amount:,.2f}" if r.actual_settlement_amount else "None",
            })
            sources.append(r.payment_id)

        return "GET_DELAYED_SETTLEMENTS", {"delayed_settlements": items}, sources

    def _tool_get_entity_detail(self, entity_id: str, db: Session) -> tuple[str, Dict[str, Any], List[str]]:
        rec = None
        if entity_id.startswith("rec_"):
            rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == entity_id).first()
        elif entity_id.startswith("pay_"):
            rec = db.query(ReconciliationResult).filter(ReconciliationResult.payment_id == entity_id).first()
        elif entity_id.startswith("inv_"):
            inv = db.query(InvestigationResult).filter(InvestigationResult.id == entity_id).first()
            if inv:
                rec = db.query(ReconciliationResult).filter(ReconciliationResult.id == inv.reconciliation_id).first()

        if not rec:
            return "GET_ENTITY_DETAIL", {"error": f"No records found matching ID '{entity_id}'"}, []

        inv = db.query(InvestigationResult).filter(InvestigationResult.reconciliation_id == rec.id).first()
        data = {
            "reconciliation_id": rec.id,
            "payment_id": rec.payment_id,
            "status": rec.status.value if hasattr(rec.status, "value") else str(rec.status),
            "classification": rec.classification,
            "expected_settlement": f"₹{rec.expected_settlement_amount:,.2f}",
            "actual_bank_credit": f"₹{rec.actual_bank_amount:,.2f}" if rec.actual_bank_amount else "None",
            "discrepancy": f"₹{rec.discrepancy_amount:,.2f}",
            "ai_investigation": {
                "status": inv.investigation_status.value if (inv and hasattr(inv.investigation_status, "value")) else "NOT_INVESTIGATED",
                "summary": inv.summary if inv else None,
                "explanation": inv.explanation if inv else None,
                "system_confidence": f"{inv.system_confidence}%" if inv else None,
            } if inv else "Not investigated yet",
        }
        return "GET_ENTITY_DETAIL", data, [rec.id, rec.payment_id]

    def _tool_get_summary_with_exceptions(self, db: Session, merchant_id: Optional[str]) -> tuple[str, Dict[str, Any], List[str]]:
        sum_data = DeterministicReconciliationEngine.compute_summary(db, merchant_id=merchant_id)
        exceptions = db.query(ReconciliationResult).filter(
            ReconciliationResult.status != "MATCHED"
        ).limit(3).all()

        ex_list = [{"reconciliation_id": e.id, "payment_id": e.payment_id, "discrepancy": f"₹{e.discrepancy_amount:,.2f}", "classification": e.classification} for e in exceptions]

        return "GET_OVERVIEW_WITH_EXCEPTIONS", {
            "total_records": sum_data.total_records,
            "match_rate": f"{sum_data.match_rate_percentage}%",
            "total_discrepancy": f"₹{sum_data.total_discrepancy_amount:,.2f}",
            "sample_exceptions": ex_list,
        }, [e.payment_id for e in exceptions]
