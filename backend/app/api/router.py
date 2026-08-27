from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.reconciliation import router as reconciliation_router

api_router = APIRouter()

# Register core sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(reconciliation_router)
