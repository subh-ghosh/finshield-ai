"""Deterministic insights engine for Knowledge Graph intelligence."""

from typing import List, Dict, Set
from app.models.graph_models import CentralityMetrics, GraphNode, GraphEdge
from app.config.graph_config import graph_config
from app.types.graph import NodeType

class GraphInsightsEngine:
    """Generates deterministic, rule-based text insights based on graph topography without LLMs."""

    def __init__(self):
        pass

    def generate_centrality_insights(self, node: GraphNode, metrics: CentralityMetrics) -> List[str]:
        """Generate insights based purely on centrality thresholds."""
        insights = []
        
        # In a real environment, these thresholds would be statistically derived
        if metrics.degree > 0.8:
            insights.append(f"{node.label} acts as an extreme structural hub within the network, highly interconnected with multiple entities.")
        elif metrics.degree > 0.3:
            insights.append(f"{node.label} exhibits high connectivity, suggesting central coordination.")
            
        if metrics.betweenness > 0.4:
            insights.append(f"{node.label} acts as a critical bridge. Its removal would shatter the network into disconnected components.")
            
        if metrics.pagerank > 0.2:
            insights.append(f"{node.label} commands significant influence. Network flow naturally funnels toward this entity.")
            
        return insights

    def generate_neighborhood_insights(
        self, focal_node: GraphNode, nodes: List[GraphNode], edges: List[GraphEdge]
    ) -> List[str]:
        """Generate insights based on the composition of the ego graph."""
        insights = []
        
        device_count = sum(1 for n in nodes if n.type == NodeType.DEVICE)
        ip_count = sum(1 for n in nodes if n.type == NodeType.IP)
        customer_count = sum(1 for n in nodes if n.type == NodeType.CUSTOMER and n.id != focal_node.id)
        
        if customer_count > 0:
            if device_count > 0 or ip_count > 0:
                insights.append(f"Entity is linked to {customer_count} other customer(s) via shared technical telemetry (Devices/IPs).")
            else:
                insights.append(f"Entity is connected to {customer_count} other customer(s) primarily through financial transactions.")
                
        # Count flagged/high-risk nodes if metadata contains risk_score
        high_risk_nodes = sum(1 for n in nodes if float(n.metadata.get("risk_score", 0.0)) >= graph_config.GRAPH_HIGH_RISK_THRESHOLD)
        if high_risk_nodes > 0:
            insights.append(f"WARNING: Neighborhood contains {high_risk_nodes} entity(ies) exceeding the high-risk threshold ({graph_config.GRAPH_HIGH_RISK_THRESHOLD}).")

        return insights

    def generate_community_insights(self, focal_node_id: str, communities: List[List[str]]) -> List[str]:
        """Generate insights about community participation."""
        insights = []
        participated_communities = [c for c in communities if focal_node_id in c]
        
        if len(participated_communities) > 1:
            insights.append(f"Entity spans {len(participated_communities)} distinct behavioral clusters, suggesting organized activity across isolated groups.")
        elif len(participated_communities) == 1:
            size = len(participated_communities[0])
            if size > graph_config.GRAPH_COMMUNITY_THRESHOLD:
                insights.append(f"Entity operates within a tight-knit cluster of {size} nodes.")
                
        return insights
