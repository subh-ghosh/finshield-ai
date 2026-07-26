from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
from app.services.graph_analysis import GraphAnalyzer

router = APIRouter(tags=["Knowledge Graph"])
analyzer = GraphAnalyzer()

@router.get(
    "/graph/{customer_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve ego graph for a specific customer"
)
def get_graph(
    customer_id: str,
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
):
    """Retrieves nodes and edges for the Knowledge Graph UI."""
    customer_id = customer_id.strip()
    
    if pipeline_res is None or pipeline_res.clean_dataframe is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pipeline result or clean transactions dataframe not found."
        )

    # Use the analyzer to build a 2-hop ego network
    graph_data = analyzer.get_ego_graph(customer_id, pipeline_res.clean_dataframe, max_hops=2)
    
    if not graph_data["nodes"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer ID '{customer_id}' has no network graph data."
        )

    return graph_data
