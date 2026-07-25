"""Pydantic v2 response schemas for REST API error, health, metrics, and profile endpoints."""

import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """Standardized HTTP error response structure."""
    error_code: str = Field(..., description="Machine readable error code string", json_schema_extra={"example": "CUSTOMER_NOT_FOUND"})
    message: str = Field(..., description="Human readable message summary", json_schema_extra={"example": "Customer ID 'C_9999' was not found"})
    details: Optional[str] = Field(None, description="Additional debug context or traceback information")
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), description="ISO 8601 timestamp")


class HealthResponse(BaseModel):
    """System health status response."""
    status: str = Field("ok", description="Service operational status")
    service: str = Field("FinShield AI Intelligence API", description="Service designation")
    version: str = Field("1.0.0", description="API version identifier")
    uptime_seconds: float = Field(..., description="Uptime duration in seconds")


class MetricsResponse(BaseModel):
    """Pipeline execution profiling metrics response."""
    total_rows: int = Field(..., description="Total dataset rows ingested")
    clean_rows: int = Field(..., description="Clean transaction records exported")
    engineered_customers: int = Field(..., description="Total engineered customer profiles")
    flagged_rules_count: int = Field(..., description="Customers flagged by rule violations")
    flagged_anomalies_count: int = Field(..., description="Customers flagged as ML outliers")
    execution_time_seconds: float = Field(..., description="Total pipeline execution duration in seconds")
    timings: Dict[str, float] = Field(default_factory=dict, description="Stage profiling breakdown timing dictionary")


class CustomerProfileResponse(BaseModel):
    """Customer profile details response."""
    customer_id: str = Field(..., description="Customer unique ID")
    feature_metrics: Dict[str, Any] = Field(..., description="Engineered behavioral feature metrics dictionary")
    rule_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of rule evaluations")
    anomaly_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of anomaly detection")
