from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rate_limiter import assistant_limiter
from app.ai.assistant import FinanceAssistant
from app.ai.schemas import AssistantQueryRequest, AssistantQueryResponse

router = APIRouter(prefix="/assistant", tags=["Finance Copilot Assistant"])


@router.post("/query", response_model=AssistantQueryResponse)
def query_finance_assistant(
    request: Request,
    req: AssistantQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Queries the natural language Finance Copilot with strict evidence grounding and predefined database tools.
    """
    assistant_limiter.check_rate_limit(request)
    assistant = FinanceAssistant()
    response = assistant.query(user_query=req.query, db=db, merchant_id=req.merchant_id)
    return response
