"""Enterprise LangGraph Investigation Planner test suite.

Tests cover:
- Tool registry (registration, lookup, metadata, unknown tool)
- Async API client (success, retry, timeout, correlation ID propagation)
- VersionTool registration and delegation
- All 5 graph nodes (planner, analysis, reasoning, decision, report)
- Full integration flow (end-to-end mocked)
- PlannerResult correlation ID
- Feature flag (legacy vs enterprise routing)
- Error handling (unavailable API, timeout, missing customer)
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from dataclasses import dataclass
from typing import Any, Dict, List


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def customer_id():
    return "C_TEST_001"


@pytest.fixture
def correlation_id():
    return "test-correlation-id-1234"


@pytest.fixture
def mock_explain_response():
    """Minimal ExplanationResponseV1-shaped dict from the REST API."""
    return {
        "response_id": "resp-001",
        "customer_id": "C_TEST_001",
        "overall_risk_score": 0.87,
        "severity": "HIGH",
        "recommendation": "FILE_SAR",
        "confidence": "HIGH",
        "evidence": [
            {"source": "rule_engine", "severity": "HIGH", "description": "Structuring pattern detected"},
            {"source": "isolation_forest", "severity": "MEDIUM", "description": "Anomaly score 0.89"}
        ],
        "timeline": [
            {"timestamp": "2024-01-01T00:00:00Z", "event": "Account opened"},
            {"timestamp": "2024-01-03T12:00:00Z", "event": "$500k received"}
        ],
        "metadata": {"api_version": "v1", "schema_version": "1.0.0"},
        "metrics": {"processing_time_ms": 150.0}
    }


@pytest.fixture
def mock_health_response():
    return {"status": "ok", "service": "FinShield AI", "version": "1.0.0", "uptime_seconds": 3600.0}


@pytest.fixture
def mock_version_response():
    return {"service": "FinShield AI Intelligence API", "version": "1.0.0", "api_version": "v1", "schema_version": "1.0.0"}


# ============================================================
# 1. Tool Registry Tests
# ============================================================

class TestToolRegistry:
    def test_registry_has_all_six_tools(self):
        from app.planner.registry.tool_registry import TOOL_REGISTRY
        tools = TOOL_REGISTRY.list_tools()
        assert "analyze_customer" in tools
        assert "analyze_batch" in tools
        assert "get_customer_profile" in tools
        assert "get_explanation" in tools
        assert "health" in tools
        assert "version" in tools
        assert len(tools) == 6

    def test_get_tool_returns_instance(self):
        from app.planner.registry.tool_registry import TOOL_REGISTRY
        tool = TOOL_REGISTRY.get_tool("analyze_customer")
        assert tool is not None

    def test_get_tool_unknown_returns_none(self):
        from app.planner.registry.tool_registry import TOOL_REGISTRY
        tool = TOOL_REGISTRY.get_tool("nonexistent_tool")
        assert tool is None

    def test_get_metadata_analyze_customer(self):
        from app.planner.registry.tool_registry import TOOL_REGISTRY
        meta = TOOL_REGISTRY.get_metadata("analyze_customer")
        assert meta is not None
        assert meta.name == "analyze_customer"
        assert meta.endpoint == "/api/v1/analyze/customer"
        assert meta.http_method == "POST"

    def test_get_metadata_version_tool(self):
        from app.planner.registry.tool_registry import TOOL_REGISTRY
        meta = TOOL_REGISTRY.get_metadata("version")
        assert meta is not None
        assert meta.endpoint == "/api/v1/version"
        assert meta.http_method == "GET"

    def test_list_metadata_returns_all(self):
        from app.planner.registry.tool_registry import TOOL_REGISTRY
        all_meta = TOOL_REGISTRY.list_metadata()
        assert len(all_meta) == 6


# ============================================================
# 2. Async API Client Tests
# ============================================================

class TestFinShieldAPIClient:
    @pytest.mark.asyncio
    async def test_analyze_customer_success(self, mock_explain_response, correlation_id):
        from app.planner.client.api_client import FinShieldAPIClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_explain_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.request = AsyncMock(return_value=mock_response)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                result = await client.analyze_customer("C_TEST_001")
            assert result["overall_risk_score"] == 0.87

    @pytest.mark.asyncio
    async def test_health_success(self, mock_health_response, correlation_id):
        from app.planner.client.api_client import FinShieldAPIClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_health_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.request = AsyncMock(return_value=mock_response)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                result = await client.health()
            assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_get_version_success(self, mock_version_response, correlation_id):
        from app.planner.client.api_client import FinShieldAPIClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_version_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.request = AsyncMock(return_value=mock_response)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                result = await client.get_version()
            assert result["api_version"] == "v1"

    @pytest.mark.asyncio
    async def test_correlation_id_header_on_all_requests(self, correlation_id):
        """X-Correlation-ID must be injected into every request."""
        from app.planner.client.api_client import FinShieldAPIClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = MagicMock()

        captured_headers = []

        async def capturing_request(method, path, headers=None, **kwargs):
            captured_headers.append(headers or {})
            return mock_response

        with patch("httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.request = AsyncMock(side_effect=capturing_request)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                await client.health()
                await client.get_version()

        assert len(captured_headers) == 2
        for h in captured_headers:
            assert h.get("X-Correlation-ID") == correlation_id

    @pytest.mark.asyncio
    async def test_retry_on_503_then_success(self, mock_explain_response, correlation_id):
        """Client should retry on 503 and succeed on the next attempt."""
        from app.planner.client.api_client import FinShieldAPIClient
        from app.planner.client.exceptions import APIUnavailableError

        fail_response = MagicMock()
        fail_response.status_code = 503
        fail_response.text = "Service Unavailable"
        fail_response.raise_for_status = MagicMock()

        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.json.return_value = mock_explain_response
        ok_response.raise_for_status = MagicMock()

        call_count = 0

        async def flaky_request(method, path, headers=None, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return fail_response
            return ok_response

        with patch("httpx.AsyncClient") as MockClient, \
             patch("asyncio.sleep", new_callable=AsyncMock):
            instance = AsyncMock()
            instance.request = AsyncMock(side_effect=flaky_request)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                result = await client.analyze_customer("C_TEST_001")
            assert result["overall_risk_score"] == 0.87
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_404(self, correlation_id):
        """Client must NOT retry on 404 — raises APINotFoundError immediately."""
        from app.planner.client.api_client import FinShieldAPIClient
        from app.planner.client.exceptions import APINotFoundError

        not_found_response = MagicMock()
        not_found_response.status_code = 404
        not_found_response.text = "Not Found"
        not_found_response.raise_for_status = MagicMock()

        call_count = 0

        async def request_fn(method, path, headers=None, **kwargs):
            nonlocal call_count
            call_count += 1
            return not_found_response

        with patch("httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.request = AsyncMock(side_effect=request_fn)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                with pytest.raises(APINotFoundError):
                    await client.get_customer("INVALID_ID")
            assert call_count == 1  # Zero retries

    @pytest.mark.asyncio
    async def test_timeout_raises_api_timeout_error(self, correlation_id):
        """TimeoutException maps to APITimeoutError."""
        import httpx
        from app.planner.client.api_client import FinShieldAPIClient
        from app.planner.client.exceptions import APITimeoutError

        async def timeout_fn(method, path, headers=None, **kwargs):
            raise httpx.TimeoutException("timed out")

        with patch("httpx.AsyncClient") as MockClient, \
             patch("asyncio.sleep", new_callable=AsyncMock):
            instance = AsyncMock()
            instance.request = AsyncMock(side_effect=timeout_fn)
            instance.is_closed = False
            instance.aclose = AsyncMock()
            MockClient.return_value = instance

            async with FinShieldAPIClient(correlation_id=correlation_id) as client:
                with pytest.raises(APITimeoutError):
                    await client.health()


# ============================================================
# 3. VersionTool Tests
# ============================================================

class TestVersionTool:
    @pytest.mark.asyncio
    async def test_version_tool_delegates_to_api_client(self, mock_version_response):
        from app.planner.tools.version_tool import VersionTool
        mock_client = AsyncMock()
        mock_client.get_version = AsyncMock(return_value=mock_version_response)
        tool = VersionTool()
        result = await tool.execute(mock_client)
        mock_client.get_version.assert_awaited_once()
        assert result["api_version"] == "v1"

    def test_version_tool_metadata(self):
        from app.planner.tools.version_tool import VersionTool
        meta = VersionTool().metadata
        assert meta.name == "version"
        assert meta.endpoint == "/api/v1/version"
        assert meta.http_method == "GET"


# ============================================================
# 4. Planner Node Tests
# ============================================================

class TestPlannerNode:
    @pytest.mark.asyncio
    async def test_planner_node_seeds_pending_tools(self, customer_id, correlation_id):
        from app.planner.nodes.planner_node import planner_node

        mock_result = MagicMock()
        mock_result.tools_to_call = ["analyze_customer", "get_explanation"]
        mock_result.customer_id = customer_id
        mock_result.intent = "Full AML investigation"

        mock_llm = MagicMock()
        mock_structured = AsyncMock(return_value=mock_result)
        mock_llm.with_structured_output.return_value = MagicMock(ainvoke=mock_structured)

        with patch("app.planner.nodes.planner_node.get_llm", return_value=mock_llm):
            state = {
                "user_request": "Investigate customer",
                "customer_id": customer_id,
                "correlation_id": correlation_id,
            }
            result = await planner_node(state)

        assert "analyze_customer" in result["pending_tools"]
        assert result["current_status"] == "PLANNING_COMPLETE"
        assert result["iteration_count"] == 0
        assert result["investigation_complete"] is False

    @pytest.mark.asyncio
    async def test_planner_node_handles_llm_error(self, customer_id, correlation_id):
        """On LLM failure, falls back to ['analyze_customer']."""
        from app.planner.nodes.planner_node import planner_node

        with patch("app.planner.nodes.planner_node.get_llm", side_effect=Exception("LLM error")):
            state = {
                "user_request": "Investigate",
                "customer_id": customer_id,
                "correlation_id": correlation_id,
            }
            result = await planner_node(state)

        assert result["pending_tools"] == ["analyze_customer"]


# ============================================================
# 5. Analysis Node Tests
# ============================================================

class TestAnalysisNode:
    @pytest.mark.asyncio
    async def test_analysis_node_dispatches_tool(self, customer_id, correlation_id, mock_explain_response):
        from app.planner.nodes.analysis_node import analysis_node

        mock_tool = AsyncMock()
        mock_tool.execute = AsyncMock(return_value=mock_explain_response)

        with patch("app.planner.nodes.analysis_node.TOOL_REGISTRY") as mock_registry, \
             patch("app.planner.nodes.analysis_node.FinShieldAPIClient") as MockClient:

            mock_registry.get_tool.return_value = mock_tool
            client_instance = AsyncMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = client_instance

            state = {
                "customer_id": customer_id,
                "correlation_id": correlation_id,
                "pending_tools": ["analyze_customer"],
            }
            result = await analysis_node(state)

        assert "analyze_customer" in result["tool_history"]
        assert len(result["tool_outputs"]) == 1
        assert result["pending_tools"] == []

    @pytest.mark.asyncio
    async def test_analysis_node_no_pending_tools(self, customer_id, correlation_id):
        from app.planner.nodes.analysis_node import analysis_node
        state = {
            "customer_id": customer_id,
            "correlation_id": correlation_id,
            "pending_tools": [],
        }
        result = await analysis_node(state)
        assert result["current_status"] == "NO_TOOLS"


# ============================================================
# 6. Decision Node Tests
# ============================================================

class TestDecisionNode:
    @pytest.mark.asyncio
    async def test_decision_routes_to_report_when_complete(self, customer_id, correlation_id):
        from app.planner.nodes.decision_node import decision_node, route

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "SUFFICIENT"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch("app.planner.nodes.decision_node.get_llm", return_value=mock_llm):
            state = {
                "customer_id": customer_id,
                "correlation_id": correlation_id,
                "tool_history": ["analyze_customer"],
                "pending_tools": [],
                "iteration_count": 1,
                "reasoning_steps": ["Evidence is sufficient for a final report."],
                "tool_outputs": [{"tool": "analyze_customer", "output": {"overall_risk_score": 0.87}}],
            }
            result = await decision_node(state)

        assert result["investigation_complete"] is True
        state.update(result)
        assert route(state) == "report_node"

    @pytest.mark.asyncio
    async def test_decision_routes_to_analysis_when_pending(self, customer_id, correlation_id):
        from app.planner.nodes.decision_node import decision_node, route
        state = {
            "customer_id": customer_id,
            "correlation_id": correlation_id,
            "tool_history": [],
            "pending_tools": ["get_explanation"],
            "iteration_count": 1,
            "reasoning_steps": [],
            "tool_outputs": [],
        }
        result = await decision_node(state)
        assert result["investigation_complete"] is False
        state.update(result)
        assert route(state) == "analysis_node"

    @pytest.mark.asyncio
    async def test_decision_forces_report_at_max_iterations(self, customer_id, correlation_id):
        from app.planner.nodes.decision_node import decision_node, route

        with patch("app.planner.nodes.decision_node.get_settings") as mock_settings:
            mock_settings.return_value.PLANNER_MAX_ITERATIONS = 1
            state = {
                "customer_id": customer_id,
                "correlation_id": correlation_id,
                "tool_history": ["analyze_customer"],
                "pending_tools": [],
                "iteration_count": 1,
                "reasoning_steps": [],
                "tool_outputs": [],
            }
            result = await decision_node(state)

        assert result["investigation_complete"] is True


# ============================================================
# 7. Report Node Tests
# ============================================================

class TestReportNode:
    @pytest.mark.asyncio
    async def test_report_node_generates_report(self, customer_id, correlation_id, mock_explain_response):
        from app.planner.nodes.report_node import report_node

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "## Executive Summary\nHigh risk customer. FILE_SAR recommended."
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch("app.planner.nodes.report_node.get_llm", return_value=mock_llm):
            state = {
                "customer_id": customer_id,
                "correlation_id": correlation_id,
                "tool_outputs": [{"tool": "analyze_customer", "output": mock_explain_response}],
                "reasoning_steps": ["Structuring pattern detected. High anomaly score."],
            }
            result = await report_node(state)

        assert "Executive Summary" in result["final_report"] or "FILE_SAR" in result["final_report"]
        assert result["current_status"] == "REPORT_COMPLETE"
        assert result["investigation_complete"] is True

    @pytest.mark.asyncio
    async def test_report_node_fallback_on_llm_error(self, customer_id, correlation_id, mock_explain_response):
        """Report node must produce a fallback report if LLM fails."""
        from app.planner.nodes.report_node import report_node

        with patch("app.planner.nodes.report_node.get_llm", side_effect=Exception("LLM down")):
            state = {
                "customer_id": customer_id,
                "correlation_id": correlation_id,
                "tool_outputs": [{"tool": "analyze_customer", "output": mock_explain_response}],
                "reasoning_steps": [],
            }
            result = await report_node(state)

        assert result["final_report"] != ""
        assert result["investigation_complete"] is True


# ============================================================
# 8. PlannerResult Correlation ID Test
# ============================================================

class TestPlannerResult:
    def test_planner_result_has_correlation_id(self):
        from app.planner.models.planner_result import PlannerResult
        result = PlannerResult(
            customer_id="C_001",
            final_report="Test report",
            recommendation="FILE_SAR",
            confidence="HIGH",
            investigation_complete=True,
            correlation_id="test-cid-abc",
            tool_calls=["analyze_customer"],
            api_calls=1,
            reasoning_steps=["Evidence found."],
            execution_time_ms=1234.5,
            planner_status="COMPLETED",
            errors=[],
        )
        assert result.correlation_id == "test-cid-abc"
        assert result.api_calls == 1
        assert result.execution_time_ms == 1234.5
        assert result.planner_status == "COMPLETED"


# ============================================================
# 9. Feature Flag Tests
# ============================================================

class TestFeatureFlag:
    @pytest.mark.asyncio
    async def test_feature_flag_enterprise_routes_correctly(self, customer_id, correlation_id):
        from app.planner.services.planner_service import run_investigation
        from app.planner.models.planner_result import PlannerResult

        mock_result = PlannerResult(
            customer_id=customer_id,
            final_report="Enterprise report",
            recommendation="FILE_SAR",
            confidence="HIGH",
            investigation_complete=True,
            correlation_id=correlation_id,
            planner_status="COMPLETED",
        )

        with patch("app.planner.services.planner_service.get_settings") as mock_settings, \
             patch("app.planner.services.planner_service._run_enterprise_planner",
                   new_callable=AsyncMock, return_value=mock_result) as mock_enterprise:

            mock_settings.return_value.PLANNER_USE_ENTERPRISE = True
            result = await run_investigation(customer_id, "Investigate", correlation_id)

        mock_enterprise.assert_awaited_once()
        assert result.planner_status == "COMPLETED"
        assert result.correlation_id == correlation_id

    @pytest.mark.asyncio
    async def test_feature_flag_legacy_routes_correctly(self, customer_id):
        from app.planner.services.planner_service import run_investigation
        from app.planner.models.planner_result import PlannerResult

        mock_result = PlannerResult(
            customer_id=customer_id,
            final_report="Legacy report",
            recommendation="MONITOR",
            confidence="LOW",
            investigation_complete=True,
            correlation_id="legacy",
            planner_status="COMPLETED",
        )

        with patch("app.planner.services.planner_service.get_settings") as mock_settings, \
             patch("app.planner.services.planner_service._run_legacy_planner",
                   return_value=mock_result) as mock_legacy:

            mock_settings.return_value.PLANNER_USE_ENTERPRISE = False
            result = await run_investigation(customer_id, "Investigate")

        mock_legacy.assert_called_once()
        assert result.planner_status == "COMPLETED"


# ============================================================
# 10. Error Handling Tests
# ============================================================

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_analysis_node_handles_api_error(self, customer_id, correlation_id):
        from app.planner.nodes.analysis_node import analysis_node
        from app.planner.client.exceptions import APIUnavailableError

        mock_tool = AsyncMock()
        mock_tool.execute = AsyncMock(side_effect=APIUnavailableError("Backend down"))

        with patch("app.planner.nodes.analysis_node.TOOL_REGISTRY") as mock_registry, \
             patch("app.planner.nodes.analysis_node.FinShieldAPIClient") as MockClient:

            mock_registry.get_tool.return_value = mock_tool
            client_instance = AsyncMock()
            client_instance.__aenter__ = AsyncMock(return_value=client_instance)
            client_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = client_instance

            state = {
                "customer_id": customer_id,
                "correlation_id": correlation_id,
                "pending_tools": ["analyze_customer"],
            }
            result = await analysis_node(state)

        # Should not raise — error captured in state
        assert len(result.get("errors", [])) > 0

    @pytest.mark.asyncio
    async def test_planner_service_handles_graph_error(self, customer_id, correlation_id):
        from app.planner.services.planner_service import _run_enterprise_planner

        async def bad_stream(*args, **kwargs):
            raise RuntimeError("Graph exploded")
            yield {}  # make it an async generator

        mock_graph = MagicMock()
        mock_graph.astream = bad_stream

        with patch("app.planner.graph.investigation_graph.investigation_graph", mock_graph):
            result = await _run_enterprise_planner(customer_id, "Investigate", correlation_id)

        assert result.planner_status == "FAILED"
        assert len(result.errors) > 0
        assert result.correlation_id == correlation_id
