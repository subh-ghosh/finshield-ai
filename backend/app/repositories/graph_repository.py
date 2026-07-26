"""Repository layer for Knowledge Graph cache management."""

from app.services.graph_adapter import IGraphAdapter
from app.services.graph_builder import GraphBuilder
from app.models.pipeline_result import PipelineResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GraphRepository:
    """Manages the graph lifecycle and avoids expensive continuous rebuilds."""

    def __init__(self, adapter: IGraphAdapter):
        self.adapter = adapter
        self._is_built = False

    def get_or_build_graph(self, pipeline_result: PipelineResult) -> IGraphAdapter:
        """
        Retrieves the built graph adapter. If not built yet, constructs it 
        using the provided cached PipelineResult.
        
        Args:
            pipeline_result: The executed and cached AML Pipeline result.
            
        Returns:
            IGraphAdapter: The initialized graph adapter.
        """
        if not self._is_built:
            logger.info("Graph cache is empty. Initiating graph build from PipelineResult...")
            builder = GraphBuilder(self.adapter)
            
            # Using the cached pandas dataframes directly from the existing pipeline
            builder.build(
                clean_dataframe=pipeline_result.clean_dataframe, 
                customer_features=pipeline_result.customer_features
            )
            self._is_built = True
            logger.info("Graph cached successfully in repository.")
        else:
            logger.debug("Returning cached graph from repository.")
            
        return self.adapter
        
    def force_rebuild(self, pipeline_result: PipelineResult) -> IGraphAdapter:
        """Forces a rebuild of the graph, clearing the current cache."""
        self.clear_cache()
        return self.get_or_build_graph(pipeline_result)
        
    def clear_cache(self) -> None:
        """Clears the current graph cache."""
        logger.info("Clearing graph repository cache.")
        self.adapter.clear()
        self._is_built = False
