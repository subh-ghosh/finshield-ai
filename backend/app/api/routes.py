"""Central API Router registering v1 endpoints and existing legacy investigation/planner routes."""

from fastapi import APIRouter
from app.api.endpoints import investigations, planner
from app.api.v1.routers.router import v1_router

router = APIRouter()

# Mount v1 REST API endpoints under /v1 (resolving to /api/v1/...)
router.include_router(v1_router, prefix="/v1")

# Legacy endpoints for backward compatibility with existing components
router.include_router(
    investigations.router, prefix="/investigations", tags=["investigations"]
)
router.include_router(planner.router, prefix="/planner", tags=["planner"])
