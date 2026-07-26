"""Pydantic data models for the Upgraded Enterprise Investigation Memory Store."""

import time
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class CaseTypology(str, Enum):
    STRUCTURING = "STRUCTURING"
    SMURFING = "SMURFING"
    LAYERING = "LAYERING"
    FUNNEL_ACCOUNT = "FUNNEL_ACCOUNT"
    MONEY_MULE = "MONEY_MULE"
    TRADE_BASED_ML = "TRADE_BASED_ML"
    HIGH_RISK_JURISDICTION = "HIGH_RISK_JURISDICTION"
    SANCTIONS = "SANCTIONS"
    SHELL_COMPANY = "SHELL_COMPANY"
    CRYPTO = "CRYPTO"
    TERRORISM_FINANCING = "TERRORISM_FINANCING"
    UNKNOWN = "UNKNOWN"


class CaseOutcome(str, Enum):
    FALSE_POSITIVE = "FALSE_POSITIVE"
    TRUE_POSITIVE = "TRUE_POSITIVE"
    SAR_FILED = "SAR_FILED"
    SAR_ACCEPTED = "SAR_ACCEPTED"
    SAR_REJECTED = "SAR_REJECTED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"
    NO_ACTION = "NO_ACTION"


class TimelineEvent(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    event_type: str
    actor: str = "SYSTEM"
    description: str
    source: str = "INVESTIGATION_PIPELINE"


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
    case_outcome: Optional[str] = "CLOSED"
    case_typology: Optional[str] = "UNKNOWN"
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
    timeline: List[TimelineEvent] = Field(default_factory=list)


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
    case_outcome: str = "CLOSED"
    case_typology: str = "UNKNOWN"
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
    timeline: List[TimelineEvent] = Field(default_factory=list)
    feature_vector: MemoryFeatureVector
    narrative_embedding: List[float] = Field(default_factory=list)
    semantic_embedding: List[float] = Field(default_factory=list)  # Alias for backward compatibility
    version: int = 1
    timestamp: float = Field(default_factory=time.time)
    is_deleted: bool = False


class MemorySearchQuery(BaseModel):
    query_text: Optional[str] = None
    customer_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    industry: Optional[str] = None
    final_decision: Optional[str] = None
    case_typology: Optional[str] = None
    case_outcome: Optional[str] = None
    min_risk_score: Optional[float] = 0.0
    max_risk_score: Optional[float] = 100.0
    limit: int = 10


class MemorySearchResult(BaseModel):
    memory_record: InvestigationMemoryRecord
    similarity_score: float
    matching_features: List[str]
