"""Model definition for customer AML risk analysis results."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from app.models.triggered_rule import TriggeredRule
from app.models.analysis_source import AnalysisSource

@dataclass
class AnalysisResult:
    """Consolidates risk evaluations, anomaly predictions, and rule-based triggers for a customer."""
    customer_id: str
    severity: str
    total_rule_score: int = 0
    triggered_rules: List[TriggeredRule] = field(default_factory=list)
    source: AnalysisSource = AnalysisSource.RULE_ENGINE
    score: float = 0.0
    confidence: float = 1.0
    anomaly_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
