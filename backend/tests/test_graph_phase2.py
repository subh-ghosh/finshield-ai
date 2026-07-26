"""Unit tests for Phase 2 Graph Builder, Adapter, and Repository."""

import pytest
import pandas as pd

from app.models.graph_models import GraphNode, GraphEdge
from app.types.graph import NodeType, RelationshipType
from app.services.graph_adapter import NetworkXAdapter
from app.services.graph_builder import GraphBuilder
from app.repositories.graph_repository import GraphRepository
from app.models.pipeline_result import PipelineResult

@pytest.fixture
def mock_pipeline_result():
    # Mock dataframes that simulate PipelineResult
    customer_features = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "risk_score": [80.0, 10.0]
    })
    
    clean_dataframe = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "sender_account": ["A1", "A2"],
        "receiver_account": ["A2", "A1"],
        "transaction_id": ["T1", "T2"],
        "amount": [100.0, 50.0],
        "currency": ["USD", "EUR"],
        "timestamp": ["2023-01-01T10:00:00Z", "2023-01-02T10:00:00Z"]
    })
    
    # Create a dummy PipelineResult
    result = PipelineResult(
        clean_dataframe=clean_dataframe,
        customer_features=customer_features,
        rule_analysis={},
        rule_dataframe=pd.DataFrame(),
        anomaly_analysis={},
        anomaly_dataframe=pd.DataFrame(),
        hybrid_risk_analysis={},
        hybrid_risk_dataframe=pd.DataFrame(),
        report=None,
        execution_time=0.1,
        pipeline_version="1.0.0",
        model_versions={},
        metadata={}
    )
    return result

def test_networkx_adapter_basic_ops():
    """Verify the adapter can add nodes/edges and fetch them."""
    adapter = NetworkXAdapter()
    
    node = GraphNode(id="n1", label="Node 1", type=NodeType.CUSTOMER)
    adapter.add_node(node)
    
    assert adapter.has_node("n1")
    fetched = adapter.get_node("n1")
    assert fetched.label == "Node 1"
    
    node2 = GraphNode(id="n2", label="Node 2", type=NodeType.ACCOUNT)
    adapter.add_node(node2)
    
    edge = GraphEdge(source="n1", target="n2", relationship=RelationshipType.OWNS_ACCOUNT)
    adapter.add_edge(edge)
    
    neighbors = adapter.get_neighbors("n1")
    assert "n2" in neighbors
    
def test_networkx_adapter_ego_graph():
    """Verify ego graph extraction works."""
    adapter = NetworkXAdapter()
    adapter.add_node(GraphNode(id="n1", label="N1", type=NodeType.CUSTOMER))
    adapter.add_node(GraphNode(id="n2", label="N2", type=NodeType.ACCOUNT))
    adapter.add_node(GraphNode(id="n3", label="N3", type=NodeType.ACCOUNT))
    
    adapter.add_edge(GraphEdge(source="n1", target="n2", relationship=RelationshipType.OWNS_ACCOUNT))
    adapter.add_edge(GraphEdge(source="n2", target="n3", relationship=RelationshipType.TRANSACTS_WITH))
    
    # Radius 1 ego graph for n1 should include n2 but not n3
    nodes, edges = adapter.get_ego_graph_data("n1", radius=1)
    
    node_ids = {n.id for n in nodes}
    assert "n1" in node_ids
    assert "n2" in node_ids
    assert "n3" not in node_ids

def test_graph_builder(mock_pipeline_result):
    """Verify builder correctly transforms dataframes into graph structure."""
    adapter = NetworkXAdapter()
    builder = GraphBuilder(adapter)
    
    builder.build(mock_pipeline_result.clean_dataframe, mock_pipeline_result.customer_features)
    
    # Should have synthesized C1, C2 and their devices/IPs + Accounts A1, A2
    assert adapter.has_node("C1")
    assert adapter.has_node("A1")
    
    # Check edges
    neighbors = adapter.get_neighbors("C1")
    assert "A1" in neighbors
    
    # Ensure Device synthesis worked
    nodes, _ = adapter.get_ego_graph_data("C1", radius=1)
    device_nodes = [n for n in nodes if n.type == NodeType.DEVICE]
    assert len(device_nodes) == 1

def test_graph_repository(mock_pipeline_result):
    """Verify repository caching logic."""
    adapter = NetworkXAdapter()
    repo = GraphRepository(adapter)
    
    # Initially empty
    assert not adapter.has_node("C1")
    
    # Get or build should build it
    g_adapter = repo.get_or_build_graph(mock_pipeline_result)
    assert g_adapter.has_node("C1")
    assert repo._is_built
    
    # Next call should use cache, let's clear adapter without changing _is_built flag 
    # to prove it doesn't rebuild (simulating caching)
    adapter.clear()
    g_adapter = repo.get_or_build_graph(mock_pipeline_result)
    assert not g_adapter.has_node("C1")  # Because it didn't rebuild
    
    # Force rebuild
    g_adapter = repo.force_rebuild(mock_pipeline_result)
    assert g_adapter.has_node("C1")
    assert repo._is_built
