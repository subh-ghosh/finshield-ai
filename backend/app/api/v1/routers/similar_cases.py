"""FastAPI Router for Enterprise Similar Historical Case Retrieval."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.similar_cases import (
    SimilarCasesResponse,
    CaseComparisonResult,
    CaseComparisonRequest
)
from app.services.similar_cases_engine import SimilarCasesEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/similar-cases", tags=["Enterprise Similar Historical Case Retrieval"])

_engine_instance = SimilarCasesEngine()


@router.get(
    "/{investigationId}",
    response_model=SimilarCasesResponse,
    summary="Retrieve Similar Historical Cases",
    description="Retrieves the top K historical cases matching the current investigation using weighted hybrid similarity."
)
async def get_similar_cases(
    investigationId: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of historical matches to return")
):
    try:
        return _engine_instance.find_similar_cases(investigation_id=investigationId, limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving similar cases for {investigationId}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve similar cases: {str(e)}"
        )


@router.post(
    "/search",
    response_model=SimilarCasesResponse,
    summary="Search Similar Cases by Custom Criteria",
    description="Executes a similarity search across institutional memory for specified investigation parameters."
)
async def search_similar_cases(body: dict):
    investigation_id = body.get("investigation_id", "C_4284")
    limit = int(body.get("limit", 5))
    return _engine_instance.find_similar_cases(investigation_id=investigation_id, limit=limit)


@router.get(
    "/{caseId}/comparison",
    response_model=CaseComparisonResult,
    summary="Get Side-by-Side Case Comparison Workspace",
    description="Generates side-by-side comparative analysis between active case and historical case."
)
async def get_case_comparison(
    caseId: str,
    historical_case_id: str = Query(..., description="Historical case ID to compare against")
):
    try:
        return _engine_instance.compare_cases(
            current_investigation_id=caseId,
            historical_case_id=historical_case_id
        )
    except Exception as e:
        logger.error(f"Error comparing cases {caseId} vs {historical_case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate case comparison: {str(e)}"
        )
