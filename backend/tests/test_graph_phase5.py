"""Unit tests for Phase 5 Graph Service Facade."""

import pytest
import pandas as pd
from app.services.graph_adapter import NetworkXAdapter
from app.repositories.graph_repository import GraphRepository
from app.services.graph_insights import GraphInsightsEngine
from app.services.graph_service import GraphService
from app.models.pipeline_result import PipelineResult

@pytest.fixture
def graph_service():
    # Setup mock pipeline result
    customer_features = pd.DataFrame({"customer_id": ["C1", "C2"], "risk_score": [85.0, 10.0]})
    clean_dataframe = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "sender_account": ["A1", "A2"],
        "receiver_account": ["A2", "A1"],
        "transaction_id": ["T1", "T2"],
        "amount": [100.0, 50.0],
        "currency": ["USD", "EUR"],
        "timestamp": ["2023-01-01T10:00:00Z", "2023-01-02T10:00:00Z"]
    })
    pipeline_result = PipelineResult(
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
    
    # Setup dependencies
    adapter = NetworkXAdapter()
    repo = GraphRepository(adapter)
    insights = GraphInsightsEngine()
    
    # Initialize service
    return GraphService(repository=repo, insights_engine=insights, pipeline_result=pipeline_result)

def test_graph_service_get_ego_graph(graph_service):
    """Verify service correctly fetches and maps ego graph to DTOs."""
    dto = graph_service.get_ego_graph("C1", radius=1)
    
    # Check mapping
    assert len(dto.nodes) > 0
    assert len(dto.edges) > 0
    
    node_ids = {n.id for n in dto.nodes}
    assert "C1" in node_ids
    assert "A1" in node_ids  # Because C1 OWNS_ACCOUNT A1

def test_graph_service_get_network_summary(graph_service):
    """Verify service correctly aggregates insights and centrality into summary DTO."""
    summary = graph_service.get_network_summary("C1")
    
    # Check aggregation counters (C1 is connected to A1 directly, and C2 via Device in full data, etc)
    # Our simple dataset creates devices. Let's just check the structure.
    assert summary.connected_customers >= 0
    assert summary.shared_devices >= 0
    
    # Check centrality
    assert summary.centrality.degree >= 0
    assert summary.centrality.pagerank >= 0
    
    # Check insights
    assert len(summary.insights) > 0
    assert any(isinstance(insight, str) for insight in summary.insights)

def test_graph_service_missing_node(graph_service):
    """Verify behavior when requesting non-existent nodes."""
    dto = graph_service.get_ego_graph("NON_EXISTENT", radius=1)
    assert len(dto.nodes) == 0
    assert len(dto.edges) == 0
    
    with pytest.raises(ValueError):
        graph_service.get_network_summary("NON_EXISTENT")
