"""Score breakdown details representing components of overall hybrid risk."""

from dataclasses import dataclass
from typing import Dict

@dataclass
class ScoreBreakdown:
    """Consolidates individual rule, ML, and behavioural risk scores along with fusion weights."""
    rule_score: float
    ml_score: float
    behavioral_score: float
    overall_score: float
    weights_used: Dict[str, float]
