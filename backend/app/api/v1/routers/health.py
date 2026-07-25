"""Health router providing service status, uptime metrics, and version information."""

import time
from fastapi import APIRouter, status
from app.api.v1.dependencies import APP_START_TIME
from app.api.v1.schemas.responses import HealthResponse

router = APIRouter(tags=["System Operations"])

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service health check",
    description="Returns service status, version, and uptime duration in seconds."
)
def get_health() -> HealthResponse:
    """Returns system health check response."""
    uptime = time.time() - APP_START_TIME
    return HealthResponse(
        status="ok",
        service="FinShield AI Intelligence API",
        version="1.0.0",
        uptime_seconds=round(uptime, 2)
    )


@router.get(
    "/version",
    status_code=status.HTTP_200_OK,
    summary="Service version metadata",
    description="Returns backend service name, version, and API version for compatibility verification."
)
def get_version() -> dict:
    """Returns service version metadata."""
    return {
        "service": "FinShield AI Intelligence API",
        "version": "1.0.0",
        "api_version": "v1",
        "schema_version": "1.0.0"
    }
