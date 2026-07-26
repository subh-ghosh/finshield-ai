"""Pydantic data models for the Enterprise Investigation Memory Store."""

import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class MemoryFeatureVector(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0)
    rule_score: float = Field(..., ge=0.0, le=1.0)
    ml_anomaly_score: float = Field(..., ge=0.0, le=1.0)
    structuring_score: float = Field(default=0.0, ge=0.0, le=1.0)
    velocity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    cash_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    cross_border_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    dense_vector: List[float] = Field(default_factory=list)


class StoreMemoryRequest(BaseModel):
    case_id: str
    customer_id: str
    customer_name: Optional[str] = "Unknown"
    customer_type: str = "INDIVIDUAL"
    industry: str = "General"
    jurisdiction: str = "Domestic"
    risk_score: float
    final_decision: str  # CLEAR, MANUAL_REVIEW, ESCALATE, FILE_SAR
    disposition: str = "CASE_CLOSED"
    triggered_rules: List[str] = Field(default_factory=list)
    behavioral_features: Dict[str, float] = Field(default_factory=dict)
    isolation_forest_score: float = 0.0
    hybrid_risk_score: float = 0.0
    network_metrics: Dict[str, Any] = Field(default_factory=dict)
    evidence_summary: List[str] = Field(default_factory=list)
    compliance_completeness_score: float = 100.0
    missing_evidence_pillars: List[str] = Field(default_factory=list)
    investigation_summary: str = ""
    sar_narrative: Optional[str] = None
    analyst_notes: Optional[str] = None
    investigation_duration_sec: float = 0.0
    case_typology: str = "UNKNOWN_TYPOLOGY"


class InvestigationMemoryRecord(BaseModel):
    memory_id: str
    case_id: str
    customer_id: str
    customer_name: str
    customer_type: str
    industry: str
    jurisdiction: str
    investigation_date: str
    risk_score: float
    final_decision: str
    disposition: str
    case_typology: str
    triggered_rules: List[str]
    behavioral_features: Dict[str, float]
    isolation_forest_score: float
    hybrid_risk_score: float
    network_metrics: Dict[str, Any]
    evidence_summary: List[str]
    compliance_completeness_score: float
    missing_evidence_pillars: List[str]
    investigation_summary: str
    sar_narrative: Optional[str]
    analyst_notes: Optional[str]
    investigation_duration_sec: float
    feature_vector: MemoryFeatureVector
    semantic_embedding: List[float] = Field(default_factory=list)
    version: int = 1
    timestamp: float = Field(default_factory=time.time)
    is_deleted: bool = False


class MemorySearchQuery(BaseModel):
    query_text: Optional[str] = None
    customer_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    industry: Optional[str] = None
    final_decision: Optional[str] = None
    min_risk_score: Optional[float] = 0.0
    max_risk_score: Optional[float] = 100.0
    limit: int = 10


class MemorySearchResult(BaseModel):
    memory_record: InvestigationMemoryRecord
    similarity_score: float
    matching_features: List[str]
