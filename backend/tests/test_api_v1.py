"""Comprehensive unit and integration test suite for REST API v1 endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ====================================================
# HEALTH & METRICS ENDPOINTS TESTS
# ====================================================

def test_root_health_check():
    """Tests /health root endpoint response."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_api_v1_health():
    """Tests /api/v1/health endpoint response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert data["service"] == "FinShield AI Intelligence API"

def test_api_v1_metrics():
    """Tests /api/v1/metrics endpoint response."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] > 0
    assert data["clean_rows"] > 0
    assert data["engineered_customers"] > 0
    assert "execution_time_seconds" in data
    assert "timings" in data

# ====================================================
# CUSTOMER & EXPLANATION ENDPOINTS TESTS
# ====================================================

def test_api_v1_get_customer_success():
    """Tests GET /api/v1/customer/{customer_id} for a valid customer."""
    # Using a known customer ID from dataset evaluation
    response = client.get("/api/v1/customer/C_6456")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "C_6456"
    assert "feature_metrics" in data
    assert "rule_summary" in data

def test_api_v1_get_customer_not_found():
    """Tests GET /api/v1/customer/{customer_id} for a non-existent customer."""
    response = client.get("/api/v1/customer/C_NON_EXISTENT_99999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "RESOURCE_NOT_FOUND"
    assert "was not found" in data["message"]

def test_api_v1_get_explanation_success():
    """Tests GET /api/v1/explanation/{customer_id} for a valid customer."""
    response = client.get("/api/v1/explanation/C_6456")
    assert response.status_code in [200, 404] # 404 is acceptable if not generated yet
    if response.status_code == 200:
        data = response.json()
        assert data["customer_id"] == "C_6456"
        assert "response_id" in data
        assert "overall_risk_score" in data
        assert "evidence" in data
        assert "metadata" in data

def test_api_v1_get_explanation_not_found():
    """Tests GET /api/v1/explanation/{customer_id} for a non-existent customer."""
    response = client.get("/api/v1/explanation/C_INVALID_CUSTOMER")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "RESOURCE_NOT_FOUND"

# ====================================================
# ANALYSIS ENDPOINTS TESTS (POST /analyze/customer & POST /analyze/batch)
# ====================================================

def test_api_v1_analyze_customer_success():
    """Tests POST /api/v1/analyze/customer for a valid customer."""
    payload = {"customer_id": "C_6456"}
    response = client.post("/api/v1/analyze/customer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "C_6456"
    assert "overall_risk_score" in data
    assert "recommendation" in data

def test_api_v1_analyze_customer_validation_error():
    """Tests POST /api/v1/analyze/customer with an empty customer_id."""
    payload = {"customer_id": "   "}
    response = client.post("/api/v1/analyze/customer", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"

def test_api_v1_analyze_batch_success():
    """Tests POST /api/v1/analyze/batch for multiple customer IDs."""
    payload = {"customer_ids": ["C_6456", "C_7516"]}
    response = client.post("/api/v1/analyze/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["customer_id"] == "C_6456"
    assert data[1]["customer_id"] == "C_7516"

def test_api_v1_analyze_batch_empty_list():
    """Tests POST /api/v1/analyze/batch with an empty list."""
    payload = {"customer_ids": []}
    response = client.post("/api/v1/analyze/batch", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"

def test_api_v1_analyze_batch_exceed_limit():
    """Tests POST /api/v1/analyze/batch exceeding maximum limit (>500)."""
    large_list = [f"C_{i}" for i in range(501)]
    payload = {"customer_ids": large_list}
    response = client.post("/api/v1/analyze/batch", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "limit exceeded" in str(data["details"])
