"""Traceability-aware evidence item containing detail scores, severity, and origin metadata."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class EvidenceItem:
    """Represents a discrete piece of evidence extracted during the pipeline run."""
    source: str  # e.g., 'RULE_ENGINE', 'ISOLATION_FOREST', 'BEHAVIORAL'
    title: str
    description: str
    severity: str
    score: float
    confidence: float
    rule_id: Optional[str] = None
    anomaly_id: Optional[str] = None
    feature_name: Optional[str] = None
    pipeline_stage: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
