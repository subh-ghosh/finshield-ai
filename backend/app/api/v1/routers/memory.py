"""FastAPI router for Enterprise Investigation Memory Store."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.investigation_memory import (
    StoreMemoryRequest,
    InvestigationMemoryRecord,
    MemorySearchQuery,
    MemorySearchResult
)
from app.services.investigation_memory_store import InvestigationMemoryStore
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/memory", tags=["Enterprise Investigation Memory Store"])

_store_instance = InvestigationMemoryStore()


@router.post(
    "/store",
    status_code=status.HTTP_201_CREATED,
    response_model=InvestigationMemoryRecord,
    summary="Store Completed Investigation into Enterprise Memory",
    description="Indexes a closed or filed investigation into institutional memory with dual-vector embeddings."
)
async def store_investigation_memory(req: StoreMemoryRequest):
    try:
        record = _store_instance.store(req)
        return record
    except Exception as e:
        logger.error(f"Failed to store investigation memory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store memory record: {str(e)}"
        )


@router.get(
    "/search",
    response_model=List[MemorySearchResult],
    summary="Search Enterprise Investigation Memory",
    description="Performs dual-vector cosine similarity search combined with metadata filters."
)
async def search_memory(
    query_text: Optional[str] = Query(None, description="Free text query e.g. 'sub-threshold cash structuring'"),
    customer_id: Optional[str] = Query(None, description="Target customer ID filter"),
    jurisdiction: Optional[str] = Query(None, description="Jurisdiction filter"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    final_decision: Optional[str] = Query(None, description="Decision filter e.g. FILE_SAR, ESCALATE"),
    min_risk_score: Optional[float] = Query(0.0, ge=0.0, le=100.0),
    max_risk_score: Optional[float] = Query(100.0, ge=0.0, le=100.0),
    limit: int = Query(10, ge=1, le=50)
):
    search_q = MemorySearchQuery(
        query_text=query_text,
        customer_id=customer_id,
        jurisdiction=jurisdiction,
        industry=industry,
        final_decision=final_decision,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
        limit=limit
    )
    return _store_instance.search(search_q)


@router.get(
    "/statistics",
    summary="Get Memory Repository Statistics",
    description="Returns aggregate metrics on institutional knowledge stored."
)
async def get_memory_statistics():
    return _store_instance.get_statistics()


@router.get(
    "/customer/{customer_id}",
    response_model=List[InvestigationMemoryRecord],
    summary="Get Memory Records by Customer ID",
    description="Retrieves all closed investigation memories for a specific customer."
)
async def get_memory_by_customer(customer_id: str):
    records = _store_instance.get_by_customer(customer_id)
    return records


@router.get(
    "/{memory_id}",
    response_model=InvestigationMemoryRecord,
    summary="Get Memory Record by Memory ID",
    description="Retrieves a specific memory record by its unique memory ID."
)
async def get_memory_by_id(memory_id: str):
    record = _store_instance.get_by_id(memory_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory record '{memory_id}' not found."
        )
    return record
