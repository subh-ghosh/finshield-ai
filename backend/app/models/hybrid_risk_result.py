"""Consolidated final assessment output containing detailed scores, indicators, and metadata."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from app.models.explanation import Explanation
from app.models.risk_factor import RiskFactor
from app.models.score_breakdown import ScoreBreakdown

@dataclass
class HybridRiskResult:
    """Consolidated assessment containing auditability details and structured scores for a customer."""
    customer_id: str
    overall_risk_score: float
    severity: str
    confidence: float
    score_breakdown: ScoreBreakdown
    triggered_rules: List[str]
    anomaly_score: float
    risk_factors: List[RiskFactor]
    recommendation: str
    explanation: Explanation
    engine_name: str = "HybridRiskEngine"
    engine_version: str = "1.0.0"
    fusion_strategy: str = "WeightedFusionStrategy"
    recommendation_strategy: str = "DeterministicRecommendationStrategy"
    pipeline_version: str = "1.0.0"
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
