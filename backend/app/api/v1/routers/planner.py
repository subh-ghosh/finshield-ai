"""Enterprise Investigation Planner REST router — POST /api/v1/planner/investigate."""

import uuid
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import List, Optional
from app.api.v1.dependencies import get_pipeline_result
from fastapi import Depends
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
    description="Runs a deterministic AML investigation for a customer via the REST API."
)
async def investigate(
    body: InvestigateRequest,
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-ID"),
    pipeline_res = Depends(get_pipeline_result)
) -> InvestigateResponse:
    """Triggers the enterprise investigation planner for a given customer."""
    from app.orchestrator.engine import InvestigationOrchestrator

    cid = x_correlation_id or str(uuid.uuid4())

    logger.info(f"[CID: {cid}] POST /planner/investigate — customer={body.customer_id}")

    # For backward compatibility with ID formats
    customer_id = body.customer_id
    if customer_id.startswith("CUST-"):
        customer_id = customer_id.replace("CUST-", "C_")

    try:
        orchestrator = InvestigationOrchestrator()
        result = await orchestrator.investigate(customer_id=customer_id, pipeline_res=pipeline_res)
    except Exception as e:
        logger.error(f"[CID: {cid}] Investigation endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

    return InvestigateResponse(
        customer_id=result.customer_id,
        correlation_id=result.correlation_id,
        planner_status="COMPLETED",
        investigation_complete=True,
        recommendation=result.recommendation,
        confidence=str(result.confidence),
        final_report=result.executive_summary or "Report generation failed.",
        tool_calls=["LoadCustomerStage", "RuleEngineStage", "IsolationForestStage", "HybridRiskStage", "EvidenceAggregationStage"],
        api_calls=1,
        reasoning_steps=[f"{evt['action']}: {evt['description']}" for evt in result.timeline],
        execution_time_ms=result.execution_time_ms,
        errors=[],
    )
