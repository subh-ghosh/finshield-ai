"""Pydantic v2 request schemas for REST API endpoints validation."""

from typing import List
from pydantic import BaseModel, Field, field_validator

class CustomerAnalysisRequest(BaseModel):
    """Request model for single customer risk analysis."""
    customer_id: str = Field(..., description="Unique customer identifier", json_schema_extra={"example": "C_1200"})

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("customer_id cannot be empty or blank")
        return v


class BatchAnalysisRequest(BaseModel):
    """Request model for batch customer risk analysis."""
    customer_ids: List[str] = Field(..., description="List of unique customer identifiers", json_schema_extra={"example": ["C_1200", "C_1201"]})

    @field_validator("customer_ids")
    @classmethod
    def validate_customer_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("customer_ids list cannot be empty")
        if len(v) > 500:
            raise ValueError("Batch size limit exceeded. Maximum 500 customer_ids per request.")
        cleaned = [cid.strip() for cid in v if cid.strip()]
        if not cleaned:
            raise ValueError("customer_ids list contains no valid IDs")
        return cleaned
