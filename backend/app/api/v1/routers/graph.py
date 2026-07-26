"""REST API Router for Knowledge Graph endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.responses import ApiResponse, ErrorResponse
from app.api.v1.schemas.graph import GraphResponseDTO, NetworkSummaryDTO
from app.api.v1.dependencies import get_graph_service
from app.services.graph_service import GraphService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Knowledge Graph"])

@router.get(
    "/graph/ego/{node_id}",
    response_model=ApiResponse[GraphResponseDTO],
    responses={404: {"model": ErrorResponse}},
    summary="Get Ego Graph",
    description="Retrieves a localized subgraph centered on the specified node."
)
def get_ego_graph(
    node_id: str,
    radius: int = 1,
    graph_service: GraphService = Depends(get_graph_service)
) -> ApiResponse[GraphResponseDTO]:
    """Returns the nodes and edges surrounding a focal entity."""
    try:
        dto = graph_service.get_ego_graph(node_id, radius)
        if not dto.nodes:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found in graph.")
        return ApiResponse(data=dto)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch ego graph for {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while processing graph.")

@router.get(
    "/graph/summary/{node_id}",
    response_model=ApiResponse[NetworkSummaryDTO],
    responses={404: {"model": ErrorResponse}},
    summary="Get Network Summary",
    description="Calculates centrality metrics and generates deterministic insights for a focal node."
)
def get_network_summary(
    node_id: str,
    graph_service: GraphService = Depends(get_graph_service)
) -> ApiResponse[NetworkSummaryDTO]:
    """Returns a deterministic network intelligence summary."""
    try:
        dto = graph_service.get_network_summary(node_id)
        return ApiResponse(data=dto)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to generate network summary for {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while analyzing graph.")
