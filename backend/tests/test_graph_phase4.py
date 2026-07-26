"""Unit tests for Phase 4 Graph Insights Engine."""

import pytest
from app.services.graph_insights import GraphInsightsEngine
from app.models.graph_models import CentralityMetrics, GraphNode, GraphEdge
from app.types.graph import NodeType, RelationshipType

def test_generate_centrality_insights():
    engine = GraphInsightsEngine()
    node = GraphNode(id="n1", label="Test Node", type=NodeType.CUSTOMER)
    
    # Test High Degree
    metrics = CentralityMetrics(degree=0.9, betweenness=0.1, pagerank=0.1)
    insights = engine.generate_centrality_insights(node, metrics)
    assert len(insights) == 1
    assert "extreme structural hub" in insights[0]
    
    # Test Bridge
    metrics_bridge = CentralityMetrics(degree=0.1, betweenness=0.5, pagerank=0.1)
    insights_bridge = engine.generate_centrality_insights(node, metrics_bridge)
    assert len(insights_bridge) == 1
    assert "critical bridge" in insights_bridge[0]

def test_generate_neighborhood_insights():
    engine = GraphInsightsEngine()
    focal = GraphNode(id="C1", label="Cust 1", type=NodeType.CUSTOMER)
    
    # Setup ego graph
    nodes = [
        focal,
        GraphNode(id="C2", label="Cust 2", type=NodeType.CUSTOMER, metadata={"risk_score": 80.0}), # High risk
        GraphNode(id="D1", label="Dev 1", type=NodeType.DEVICE)
    ]
    edges = [
        GraphEdge(source="C1", target="D1", relationship=RelationshipType.USES_DEVICE),
        GraphEdge(source="C2", target="D1", relationship=RelationshipType.USES_DEVICE)
    ]
    
    insights = engine.generate_neighborhood_insights(focal, nodes, edges)
    
    assert any("shared technical telemetry" in i for i in insights)
    assert any("WARNING: Neighborhood contains 1 entity(ies) exceeding" in i for i in insights)

def test_generate_community_insights():
    engine = GraphInsightsEngine()
    
    # Participates in multiple communities
    insights = engine.generate_community_insights("C1", [["C1", "C2"], ["C1", "C3", "C4"]])
    assert len(insights) == 1
    assert "spans 2 distinct behavioral clusters" in insights[0]
    
    # Large single community (assuming threshold is 3 in config)
    insights_large = engine.generate_community_insights("C1", [["C1", "C2", "C3", "C4", "C5"]])
    assert len(insights_large) == 1
    assert "tight-knit cluster of 5 nodes" in insights_large[0]
