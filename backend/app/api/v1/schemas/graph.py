"""DTOs for Knowledge Graph API endpoints."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GraphNodeDTO(BaseModel):
    """Data Transfer Object representing a node in the graph."""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Human-readable node label")
    type: str = Field(..., description="Node type category (e.g., CUSTOMER, TRANSACTION)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional node properties")

class GraphEdgeDTO(BaseModel):
    """Data Transfer Object representing a directed edge in the graph."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Type of relationship")
    weight: float = Field(1.0, description="Edge weight or strength")
    timestamp: Optional[str] = Field(None, description="Temporal aspect of relationship")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional edge properties")

class GraphResponseDTO(BaseModel):
    """Payload representing a complete or partial graph structure."""
    nodes: List[GraphNodeDTO] = Field(default_factory=list, description="List of graph nodes")
    edges: List[GraphEdgeDTO] = Field(default_factory=list, description="List of graph edges")

class CentralityMetricsDTO(BaseModel):
    """Payload representing network centrality metrics."""
    degree: float = Field(..., description="Degree centrality")
    betweenness: float = Field(..., description="Betweenness centrality")
    pagerank: float = Field(..., description="PageRank score")

class NetworkSummaryDTO(BaseModel):
    """Payload representing aggregated intelligence about a specific node's network."""
    connected_customers: int = Field(0, description="Count of directly/indirectly connected customers")
    shared_devices: int = Field(0, description="Count of shared device IDs")
    shared_ips: int = Field(0, description="Count of shared IP addresses")
    shared_phones: int = Field(0, description="Count of shared phone numbers")
    connected_companies: int = Field(0, description="Count of linked companies")
    connected_directors: int = Field(0, description="Count of linked directors")
    communities: int = Field(0, description="Number of distinct communities node participates in")
    high_risk_connections: int = Field(0, description="Number of connected nodes flagged as high-risk")
    centrality: CentralityMetricsDTO = Field(..., description="Centrality scores for the focal node")
    insights: List[str] = Field(default_factory=list, description="Deterministic AI Network Insights")
