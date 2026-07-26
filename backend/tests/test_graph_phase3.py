"""Unit tests for Phase 3 Graph Analyzer."""

import pytest
from app.services.graph_analysis import KnowledgeGraphAnalyzer
from app.services.graph_adapter import NetworkXAdapter
from app.models.graph_models import GraphNode, GraphEdge
from app.types.graph import NodeType, RelationshipType

@pytest.fixture
def test_adapter():
    adapter = NetworkXAdapter()
    adapter.add_node(GraphNode(id="n1", label="N1", type=NodeType.CUSTOMER))
    adapter.add_node(GraphNode(id="n2", label="N2", type=NodeType.ACCOUNT))
    adapter.add_node(GraphNode(id="n3", label="N3", type=NodeType.ACCOUNT))
    adapter.add_node(GraphNode(id="n4", label="N4", type=NodeType.CUSTOMER))
    
    adapter.add_edge(GraphEdge(source="n1", target="n2", relationship=RelationshipType.OWNS_ACCOUNT))
    adapter.add_edge(GraphEdge(source="n2", target="n3", relationship=RelationshipType.TRANSACTS_WITH))
    adapter.add_edge(GraphEdge(source="n4", target="n3", relationship=RelationshipType.OWNS_ACCOUNT))
    
    return adapter

def test_knowledge_graph_analyzer_ego_graph(test_adapter):
    """Verify ego graph extraction via analyzer."""
    analyzer = KnowledgeGraphAnalyzer(test_adapter)
    nodes, edges = analyzer.get_ego_graph("n1", radius=1)
    
    # n1 -> n2 so n1 and n2 are in radius 1. n3 is at radius 2.
    node_ids = {n.id for n in nodes}
    assert "n1" in node_ids
    assert "n2" in node_ids
    assert "n3" not in node_ids

def test_knowledge_graph_analyzer_centrality(test_adapter):
    """Verify centrality metrics calculation."""
    analyzer = KnowledgeGraphAnalyzer(test_adapter)
    metrics = analyzer.calculate_centrality("n3")
    
    assert metrics.degree > 0
    assert metrics.pagerank > 0
    assert isinstance(metrics.betweenness, float)

def test_knowledge_graph_analyzer_shortest_path(test_adapter):
    """Verify shortest path between nodes."""
    analyzer = KnowledgeGraphAnalyzer(test_adapter)
    path = analyzer.find_shortest_path("n1", "n4")
    
    # n1 -> n2 -> n3 <- n4
    assert len(path) == 4
    assert path[0].id == "n1"
    assert path[-1].id == "n4"

def test_knowledge_graph_analyzer_connected_entities(test_adapter):
    """Verify connected entities retrieval."""
    analyzer = KnowledgeGraphAnalyzer(test_adapter)
    connected = analyzer.get_connected_entities("n2")
    
    node_ids = {n.id for n in connected}
    # n2 is connected to n1 (incoming) and n3 (outgoing)
    assert "n1" in node_ids
    assert "n3" in node_ids
    
def test_knowledge_graph_analyzer_communities(test_adapter):
    """Verify community detection."""
    analyzer = KnowledgeGraphAnalyzer(test_adapter)
    communities = analyzer.get_communities()
    
    # Should find at least one community containing all 4 nodes since they are connected
    assert len(communities) >= 1
    total_nodes_in_communities = sum(len(c) for c in communities)
    assert total_nodes_in_communities == 4
