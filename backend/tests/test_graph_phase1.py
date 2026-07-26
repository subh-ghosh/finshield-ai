"""Unit tests for Phase 1 Graph Types, Configuration, and Models."""

import pytest
from app.types.graph import NodeType, RelationshipType
from app.models.graph_models import GraphNode, GraphEdge, FinancialGraph
from app.config.graph_config import graph_config
from app.api.v1.schemas.graph import GraphNodeDTO
from app.api.v1.schemas.responses import ApiResponse

def test_node_type_enum():
    """Verify NodeType enumeration contains expected values."""
    assert NodeType.CUSTOMER == "CUSTOMER"
    assert NodeType.TRANSACTION == "TRANSACTION"

def test_relationship_type_enum():
    """Verify RelationshipType enumeration contains expected values."""
    assert RelationshipType.OWNS_ACCOUNT == "OWNS_ACCOUNT"
    assert RelationshipType.TRANSACTS_WITH == "TRANSACTS_WITH"

def test_graph_config_singleton():
    """Verify graph configuration is loaded correctly."""
    assert isinstance(graph_config.GRAPH_MAX_HOPS, int)
    assert graph_config.GRAPH_CACHE_TTL_SECONDS > 0

def test_graph_models_validation():
    """Verify domain model validation works."""
    node = GraphNode(id="n1", label="Test Node", type=NodeType.CUSTOMER)
    assert node.id == "n1"
    assert node.type == NodeType.CUSTOMER
    
    edge = GraphEdge(source="n1", target="n2", relationship=RelationshipType.OWNS_ACCOUNT)
    assert edge.weight == 1.0

def test_api_response_generic():
    """Verify the generic API response wrapper."""
    node_dto = GraphNodeDTO(id="n1", label="Dto Node", type="CUSTOMER")
    response = ApiResponse[GraphNodeDTO](data=node_dto)
    
    assert response.success is True
    assert response.version == 1
    assert response.data.id == "n1"
