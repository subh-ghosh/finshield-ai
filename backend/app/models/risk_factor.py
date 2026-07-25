"""Risk factor model representing structured evidence for risk assessments."""

from dataclasses import dataclass

@dataclass
class RiskFactor:
    """Represents a specific trigger or anomaly metric contributing to the overall threat score."""
    name: str
    score: float
    severity: str
    description: str
    source: str  # Must support: 'RULE_ENGINE', 'ISOLATION_FOREST', 'BEHAVIORAL'
