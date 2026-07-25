from fastapi import APIRouter
from app.api.endpoints import investigations, planner

router = APIRouter()
router.include_router(
    investigations.router, prefix="/investigations", tags=["investigations"]
)
router.include_router(planner.router, prefix="/planner", tags=["planner"])
