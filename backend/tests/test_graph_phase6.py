"""Unit tests for Phase 6 REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.dependencies import get_graph_service
from app.services.graph_service import GraphService
from app.api.v1.schemas.graph import GraphResponseDTO, NetworkSummaryDTO, CentralityMetricsDTO

# Mock the GraphService
class MockGraphService:
    def get_ego_graph(self, node_id: str, radius: int = 1) -> GraphResponseDTO:
        if node_id == "NON_EXISTENT":
            return GraphResponseDTO(nodes=[], edges=[])
        from app.api.v1.schemas.graph import GraphNodeDTO
        return GraphResponseDTO(nodes=[GraphNodeDTO(id="C1", label="Node", type="CUSTOMER")], edges=[])
        
    def get_network_summary(self, node_id: str) -> NetworkSummaryDTO:
        if node_id == "NON_EXISTENT":
            raise ValueError(f"Node {node_id} does not exist in the graph.")
        return NetworkSummaryDTO(
            connected_customers=2,
            shared_devices=1,
            shared_ips=0,
            shared_phones=0,
            connected_companies=0,
            connected_directors=0,
            communities=1,
            high_risk_connections=0,
            centrality=CentralityMetricsDTO(degree=1.0, betweenness=0.5, pagerank=0.2),
            insights=["Mock insight"]
        )

def override_get_graph_service():
    return MockGraphService()

app.dependency_overrides[get_graph_service] = override_get_graph_service

client = TestClient(app)

def test_get_ego_graph_api():
    """Test the ego graph endpoint."""
    response = client.get("/api/v1/graph/ego/C1?radius=1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data

def test_get_ego_graph_api_not_found():
    """Test 404 behavior for ego graph."""
    response = client.get("/api/v1/graph/ego/NON_EXISTENT?radius=1")
    assert response.status_code == 404

def test_get_network_summary_api():
    """Test the network summary endpoint."""
    response = client.get("/api/v1/graph/summary/C1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["connected_customers"] == 2
    assert "Mock insight" in data["data"]["insights"]

def test_get_network_summary_api_not_found():
    """Test 404 behavior for network summary."""
    response = client.get("/api/v1/graph/summary/NON_EXISTENT")
    assert response.status_code == 404
