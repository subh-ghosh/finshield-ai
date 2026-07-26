"""Domain models for the Knowledge Graph Intelligence module."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.types.graph import NodeType, RelationshipType

class GraphNode(BaseModel):
    """Domain representation of a node in the financial graph."""
    id: str
    label: str
    type: NodeType
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    """Domain representation of an edge (relationship) in the financial graph."""
    source: str
    target: str
    relationship: RelationshipType
    weight: float = 1.0
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphCommunity(BaseModel):
    """Domain representation of a detected community within the graph."""
    community_id: int
    nodes: List[str]
    is_suspicious: bool = False
    risk_score: float = 0.0

class CentralityMetrics(BaseModel):
    """Domain representation of node centrality metrics."""
    degree: float
    betweenness: float
    pagerank: float

class FinancialGraph(BaseModel):
    """Internal business model encapsulating a full or partial network graph."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
