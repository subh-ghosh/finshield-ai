"""Shared async HTTP client for the FinShield REST API with retry, timeout, and correlation ID support."""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional

import httpx

from app.planner.client.exceptions import (
    APINotFoundError,
    APITimeoutError,
    APIUnavailableError,
    APIValidationError,
)
from app.planner.config.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# HTTP status codes that should trigger a retry
_RETRYABLE_STATUS_CODES = {502, 503, 504}

# HTTP status codes that represent non-retryable client errors
_CLIENT_ERROR_STATUS_CODES = {400, 404, 422}


class FinShieldAPIClient:
    """Shared async HTTP client providing all REST API interactions.

    Responsibilities:
    - Shared httpx.AsyncClient with connection pooling and keep-alive
    - X-Correlation-ID propagation on every outgoing request
    - Configurable exponential backoff retry for transient failures
    - Typed exception mapping
    - Structured latency logging per call
    """

    def __init__(self, correlation_id: Optional[str] = None):
        """Initializes the API client with optional Correlation ID.

        Args:
            correlation_id: Optional UUID string to propagate across all requests.
        """
        self._settings = get_settings()
        self._correlation_id = correlation_id or ""
        self._client: Optional[httpx.AsyncClient] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "FinShieldAPIClient":
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        api_key = os.environ.get("API_KEY")
        if api_key:
            headers["X-API-Key"] = api_key

        self._client = httpx.AsyncClient(
            base_url=self._settings.FINSHIELD_API_BASE_URL,
            timeout=httpx.Timeout(self._settings.PLANNER_REQUEST_TIMEOUT),
            headers=headers,
        )
        logger.info(f"[CID: {self._correlation_id}] FinShieldAPIClient session opened â†’ {self._settings.FINSHIELD_API_BASE_URL}")
        return self

    async def __aexit__(self, *args) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.info(f"[CID: {self._correlation_id}] FinShieldAPIClient session closed.")

    # ------------------------------------------------------------------
    # Core request dispatcher with retry
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Executes an HTTP request with exponential backoff retry.

        Args:
            method: HTTP verb (GET, POST, etc.)
            path: URL path (appended to base URL)
            **kwargs: Passed directly to httpx request

        Returns:
            Parsed JSON response dict.
        """
        if self._client is None:
            raise RuntimeError("FinShieldAPIClient must be used as an async context manager.")

        headers = kwargs.pop("headers", {})
        if self._settings.PLANNER_PROPAGATE_CORRELATION_ID and self._correlation_id:
            headers["X-Correlation-ID"] = self._correlation_id

        retry_count = self._settings.PLANNER_RETRY_COUNT
        last_error: Optional[Exception] = None

        for attempt in range(retry_count + 1):
            start = time.perf_counter()
            try:
                response = await self._client.request(method, path, headers=headers, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000.0

                logger.info(
                    f"[CID: {self._correlation_id}] {method} {path} â†’ {response.status_code} ({elapsed_ms:.2f}ms)"
                )

                # Map client errors â€” never retried
                if response.status_code == 404:
                    raise APINotFoundError(
                        f"Resource not found at {path}", status_code=404
                    )
                if response.status_code in (400, 422):
                    raise APIValidationError(
                        f"Validation error from {path}: {response.text}", status_code=response.status_code
                    )

                # Map server errors â€” retryable
                if response.status_code in _RETRYABLE_STATUS_CODES:
                    raise APIUnavailableError(
                        f"Server error {response.status_code} at {path}", status_code=response.status_code
                    )

                response.raise_for_status()
                return response.json()

            except (APINotFoundError, APIValidationError):
                raise  # Non-retryable â€” propagate immediately

            except httpx.TimeoutException as exc:
                last_error = APITimeoutError(f"Request to {path} timed out: {exc}")
                logger.warning(
                    f"[CID: {self._correlation_id}] Timeout on {method} {path} (attempt {attempt + 1}/{retry_count + 1})"
                )

            except (httpx.ConnectError, httpx.RemoteProtocolError) as exc:
                last_error = APIUnavailableError(f"Connection error for {path}: {exc}")
                logger.warning(
                    f"[CID: {self._correlation_id}] Connection error on {method} {path} (attempt {attempt + 1}/{retry_count + 1})"
                )

            except APIUnavailableError as exc:
                last_error = exc
                logger.warning(
                    f"[CID: {self._correlation_id}] Retryable server error on {method} {path} (attempt {attempt + 1}/{retry_count + 1})"
                )

            if attempt < retry_count:
                backoff = min(0.5 * (2 ** attempt), 8.0)
                logger.info(f"[CID: {self._correlation_id}] Retrying in {backoff:.1f}s...")
                await asyncio.sleep(backoff)

        raise last_error or APIUnavailableError(f"All {retry_count + 1} attempts failed for {path}")

    # ------------------------------------------------------------------
    # Public API Methods
    # ------------------------------------------------------------------

    async def analyze_customer(self, customer_id: str) -> Dict[str, Any]:
        """POST /api/v1/analyze/customer"""
        return await self._request("POST", "/api/v1/analyze/customer", json={"customer_id": customer_id})

    async def analyze_batch(self, customer_ids: List[str]) -> List[Dict[str, Any]]:
        """POST /api/v1/analyze/batch"""
        return await self._request("POST", "/api/v1/analyze/batch", json={"customer_ids": customer_ids})

    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """GET /api/v1/customer/{customer_id}"""
        return await self._request("GET", f"/api/v1/customer/{customer_id}")

    async def get_explanation(self, customer_id: str) -> Dict[str, Any]:
        """GET /api/v1/explanation/{customer_id}"""
        return await self._request("GET", f"/api/v1/explanation/{customer_id}")

    async def health(self) -> Dict[str, Any]:
        """GET /api/v1/health"""
        return await self._request("GET", "/api/v1/health")

    async def get_version(self) -> Dict[str, Any]:
        """GET /api/v1/version"""
        return await self._request("GET", "/api/v1/version")

    async def get_eda_summary(self) -> Dict[str, Any]:
        """GET /api/v1/eda/summary - dataset-level EDA stats."""
        return await self._request("GET", "/api/v1/eda/summary")

    async def get_customer_features(self, customer_id: str) -> Dict[str, Any]:
        """GET /api/v1/features/{customer_id} - AML feature vector."""
        return await self._request("GET", f"/api/v1/features/{customer_id}")

    async def get_customer_anomaly(self, customer_id: str) -> Dict[str, Any]:
        """GET /api/v1/anomaly/{customer_id} - Isolation Forest anomaly score."""
        return await self._request("GET", f"/api/v1/anomaly/{customer_id}")

    async def get_risk_classification(self, customer_id: str) -> Dict[str, Any]:
        """GET /api/v1/risk-classify/{customer_id} - Hybrid risk classification."""
        return await self._request("GET", f"/api/v1/risk-classify/{customer_id}")
