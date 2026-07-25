"""Enterprise Investigation Planner REST router — POST /api/v1/planner/investigate."""

import uuid
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import List, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Investigation Planner"])


class InvestigateRequest(BaseModel):
    """Request model for triggering an AML investigation."""
    customer_id: str = Field(..., description="Target customer identifier.", examples=["C_1200"])
    request: str = Field(
        default="Perform a full AML investigation for this customer.",
        description="Natural language investigation request."
    )
    use_enterprise: Optional[bool] = Field(
        default=None,
        description="Override PLANNER_USE_ENTERPRISE setting for this request."
    )


class InvestigateResponse(BaseModel):
    """Response model for investigation results."""
    customer_id: str
    correlation_id: str
    planner_status: str
    investigation_complete: bool
    recommendation: str
    confidence: str
    final_report: str
    tool_calls: List[str]
    api_calls: int
    reasoning_steps: List[str]
    execution_time_ms: float
    errors: List[str]


@router.post(
    "/planner/investigate",
    response_model=InvestigateResponse,
    status_code=status.HTTP_200_OK,
    summary="Enterprise AML Investigation",
    description="Runs a LangGraph-orchestrated AML investigation for a customer via the REST API."
)
async def investigate(
    body: InvestigateRequest,
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-ID")
) -> InvestigateResponse:
    """Triggers the enterprise investigation planner for a given customer."""
    from app.planner.config.config import get_settings
    from app.planner.services.planner_service import run_investigation

    cid = x_correlation_id or str(uuid.uuid4())
    settings = get_settings()

    logger.info(f"[CID: {cid}] POST /planner/investigate — customer={body.customer_id}")

    # Optional per-request feature flag override
    if body.use_enterprise is not None:
        import os
        os.environ["PLANNER_USE_ENTERPRISE"] = str(body.use_enterprise).lower()
        from functools import lru_cache
        from app.planner.config.config import get_settings as _gs
        _gs.cache_clear()  # type: ignore

    try:
        result = await run_investigation(
            customer_id=body.customer_id,
            user_request=body.request,
            correlation_id=cid,
        )
    except Exception as e:
        logger.error(f"[CID: {cid}] Investigation endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

    return InvestigateResponse(
        customer_id=result.customer_id,
        correlation_id=result.correlation_id,
        planner_status=result.planner_status,
        investigation_complete=result.investigation_complete,
        recommendation=result.recommendation,
        confidence=result.confidence,
        final_report=result.final_report,
        tool_calls=result.tool_calls,
        api_calls=result.api_calls,
        reasoning_steps=result.reasoning_steps,
        execution_time_ms=result.execution_time_ms,
        errors=result.errors,
    )
