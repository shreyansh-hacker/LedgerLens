from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.reconciliation import router as reconciliation_router
from app.api.anomaly import router as anomaly_router
from app.api.investigation import router as investigation_router
from app.api.assistant import router as assistant_router

api_router = APIRouter()

# Register core sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(reconciliation_router)
api_router.include_router(anomaly_router)
api_router.include_router(investigation_router)
api_router.include_router(assistant_router)
