"""Pydantic data models for the Missing Evidence & Compliance Gap Detector."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CompliancePillar(str, Enum):
    KYC_VERIFICATION = "KYC_VERIFICATION"
    SOURCE_OF_FUNDS = "SOURCE_OF_FUNDS"
    BENEFICIAL_OWNERSHIP = "BENEFICIAL_OWNERSHIP"
    TRANSACTION_EVIDENCE = "TRANSACTION_EVIDENCE"
    NETWORK_ANALYSIS = "NETWORK_ANALYSIS"
    RULE_VALIDATION = "RULE_VALIDATION"
    EXTERNAL_VERIFICATION = "EXTERNAL_VERIFICATION"
    ANALYST_NOTES = "ANALYST_NOTES"


class EvidenceItemStatus(str, Enum):
    PRESENT = "PRESENT"
    MISSING_CRITICAL = "MISSING_CRITICAL"
    MISSING_OPTIONAL = "MISSING_OPTIONAL"
    WARNING = "WARNING"


class GapSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ComplianceItemEvaluation(BaseModel):
    pillar: CompliancePillar
    name: str
    status: EvidenceItemStatus
    weight: float = Field(..., ge=0.0, le=1.0)
    is_required_for_sar: bool = True
    description: str
    remediation_action: str


class EvidenceGapAssessment(BaseModel):
    customer_id: str
    completeness_score: float = Field(..., ge=0.0, le=100.0)
    sar_filing_ready: bool
    blocking_critical_gaps_count: int
    total_items_evaluated: int
    passed_items_count: int
    evaluations: List[ComplianceItemEvaluation]
    warnings: List[str]
    missing_critical_items: List[str]
    missing_optional_items: List[str]
    remediation_roadmap: List[str]
