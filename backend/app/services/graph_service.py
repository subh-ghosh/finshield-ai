"""Service facade for orchestrating graph operations and DTO mapping."""

from typing import List, Dict, Any
from app.utils.logger import get_logger
from app.repositories.graph_repository import GraphRepository
from app.services.graph_analysis import KnowledgeGraphAnalyzer
from app.services.graph_insights import GraphInsightsEngine
from app.models.pipeline_result import PipelineResult
from app.types.graph import NodeType
from app.api.v1.schemas.graph import (
    GraphResponseDTO, 
    GraphNodeDTO, 
    GraphEdgeDTO,
    NetworkSummaryDTO,
    CentralityMetricsDTO
)

logger = get_logger(__name__)

class GraphService:
    """Single entry point for the REST API to interact with the graph subsystem."""

    def __init__(
        self, 
        repository: GraphRepository,
        insights_engine: GraphInsightsEngine,
        pipeline_result: PipelineResult
    ):
        self.repository = repository
        self.insights_engine = insights_engine
        
        # Ensure graph is built (cache hit or miss) and initialize the analyzer
        self.adapter = self.repository.get_or_build_graph(pipeline_result)
        self.analyzer = KnowledgeGraphAnalyzer(self.adapter)

    def get_ego_graph(self, node_id: str, radius: int = 1) -> GraphResponseDTO:
        """Retrieves an ego graph and maps it to API DTOs."""
        logger.info(f"Fetching ego graph for node {node_id} (radius={radius})")
        
        if not self.adapter.has_node(node_id):
            return GraphResponseDTO(nodes=[], edges=[])
            
        nodes, edges = self.analyzer.get_ego_graph(node_id, radius)
        
        node_dtos = [
            GraphNodeDTO(id=n.id, label=n.label, type=n.type.value, metadata=n.metadata)
            for n in nodes
        ]
        edge_dtos = [
            GraphEdgeDTO(
                source=e.source, 
                target=e.target, 
                relationship=e.relationship.value, 
                weight=e.weight,
                timestamp=e.timestamp,
                metadata=e.metadata
            )
            for e in edges
        ]
        
        return GraphResponseDTO(nodes=node_dtos, edges=edge_dtos)

    def get_network_summary(self, node_id: str) -> NetworkSummaryDTO:
        """Aggregates centrality, communities, and deterministic insights for a specific node."""
        logger.info(f"Generating network summary for node {node_id}")
        
        if not self.adapter.has_node(node_id):
            raise ValueError(f"Node {node_id} does not exist in the graph.")
            
        # 1. Get raw graph data
        focal_node = self.adapter.get_node(node_id)
        nodes, edges = self.analyzer.get_ego_graph(node_id, radius=2) # Fetch wider area for metrics
        
        # 2. Run graph algorithms
        centrality = self.analyzer.calculate_centrality(node_id)
        communities = self.analyzer.get_communities()
        
        # 3. Calculate aggregation counters
        connected_customers = sum(1 for n in nodes if n.type == NodeType.CUSTOMER and n.id != node_id)
        shared_devices = sum(1 for n in nodes if n.type == NodeType.DEVICE)
        shared_ips = sum(1 for n in nodes if n.type == NodeType.IP)
        shared_phones = sum(1 for n in nodes if n.type == NodeType.PHONE)
        connected_companies = sum(1 for n in nodes if n.type == NodeType.COMPANY)
        connected_directors = sum(1 for n in nodes if n.type == NodeType.DIRECTOR)
        high_risk_connections = sum(1 for n in nodes if float(n.metadata.get("risk_score", 0.0)) >= 75.0 and n.id != node_id)
        
        participated_communities = [c for c in communities if node_id in c]
        
        # 4. Generate deterministic insights
        insights = []
        insights.extend(self.insights_engine.generate_centrality_insights(focal_node, centrality))
        insights.extend(self.insights_engine.generate_neighborhood_insights(focal_node, nodes, edges))
        insights.extend(self.insights_engine.generate_community_insights(node_id, communities))
        
        # 5. Map to DTO
        return NetworkSummaryDTO(
            connected_customers=connected_customers,
            shared_devices=shared_devices,
            shared_ips=shared_ips,
            shared_phones=shared_phones,
            connected_companies=connected_companies,
            connected_directors=connected_directors,
            communities=len(participated_communities),
            high_risk_connections=high_risk_connections,
            centrality=CentralityMetricsDTO(
                degree=centrality.degree,
                betweenness=centrality.betweenness,
                pagerank=centrality.pagerank
            ),
            insights=insights
        )
