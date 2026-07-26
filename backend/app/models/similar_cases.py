"""Pydantic data models for Enterprise Similar Historical Case Retrieval."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.models.investigation_memory import InvestigationMemoryRecord, MemoryFeatureVector, TimelineEvent


class SimilarityBreakdown(BaseModel):
    feature_vector_similarity: float = Field(..., ge=0.0, le=100.0)
    narrative_similarity: float = Field(..., ge=0.0, le=100.0)
    rule_overlap_score: float = Field(..., ge=0.0, le=100.0)
    typology_match_score: float = Field(..., ge=0.0, le=100.0)
    customer_profile_similarity: float = Field(..., ge=0.0, le=100.0)
    jurisdiction_similarity: float = Field(..., ge=0.0, le=100.0)
    timeline_similarity: float = Field(..., ge=0.0, le=100.0)
    overall_similarity_score: float = Field(..., ge=0.0, le=100.0)


class SimilarCaseResult(BaseModel):
    case_id: str
    customer_id: str
    customer_name: str
    risk_score: float
    final_decision: str
    case_outcome: str
    case_typology: str
    investigation_date: str
    investigation_duration_sec: float
    estimated_analyst_time_saved_min: int = 35
    primary_rules: List[str]
    similarity_breakdown: SimilarityBreakdown
    deterministic_reasons: List[str]
    memory_record: InvestigationMemoryRecord


class SimilarCasesResponse(BaseModel):
    current_investigation_id: str
    total_matches_found: int
    executive_similarity_summary: str
    average_similarity_pct: float
    similar_cases: List[SimilarCaseResult]


class CaseComparisonRequest(BaseModel):
    current_investigation_id: str
    historical_case_id: str


class CaseComparisonResult(BaseModel):
    current_investigation_id: str
    historical_case_id: str
    overall_similarity_pct: float
    executive_comparison_summary: str
    risk_score_comparison: Dict[str, float]
    decision_comparison: Dict[str, str]
    typology_comparison: Dict[str, str]
    rules_comparison: Dict[str, List[str]]
    matching_indicators: List[str]
    difference_highlights: List[str]
