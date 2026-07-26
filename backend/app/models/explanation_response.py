"""Versioned API contract for case explanations containing audit metadata and validation checks."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from app.models.evidence_item import EvidenceItem
from app.models.timeline_event import TimelineEvent

@dataclass
class ExplanationResponseV1:
    """Consolidated case assessment response conforming to stable API v1 specs."""
    response_id: str
    customer_id: str
    overall_risk_score: float
    severity: str
    confidence: float
    summary: str
    recommendation: str
    risk_breakdown: Dict[str, float]
    evidence: List[EvidenceItem]
    explanation: Dict[str, Any]
    timeline: List[TimelineEvent]
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Enforces mandatory fields validation and schema constraints."""
        import numpy as np
        def _clean_numpy(obj):
            if isinstance(obj, dict):
                return {k: _clean_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_clean_numpy(v) for v in obj]
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return _clean_numpy(obj.tolist())
            return obj

        self.risk_breakdown = _clean_numpy(self.risk_breakdown)
        self.explanation = _clean_numpy(self.explanation)
        self.metadata = _clean_numpy(self.metadata)
        self.metrics = _clean_numpy(self.metrics)
        if not self.response_id:
            raise ValueError("ExplanationResponseV1 validation failed: response_id is missing or empty.")
        if not self.customer_id:
            raise ValueError("ExplanationResponseV1 validation failed: customer_id is missing or empty.")
        if self.overall_risk_score is None:
            raise ValueError("ExplanationResponseV1 validation failed: overall_risk_score is missing.")
        if not self.severity:
            raise ValueError("ExplanationResponseV1 validation failed: severity is missing or empty.")
        if self.confidence is None:
            raise ValueError("ExplanationResponseV1 validation failed: confidence is missing.")
        if not self.summary:
            raise ValueError("ExplanationResponseV1 validation failed: summary is missing or empty.")
        if not self.recommendation:
            raise ValueError("ExplanationResponseV1 validation failed: recommendation is missing or empty.")
        if self.evidence is None:
            raise ValueError("ExplanationResponseV1 validation failed: evidence list is missing.")
        if not self.metadata:
            raise ValueError("ExplanationResponseV1 validation failed: metadata is missing.")
        
        # Verify required keys in metadata
        required_meta_keys = ["api_version", "schema_version", "generated_at", "generator"]
        for key in required_meta_keys:
            if key not in self.metadata:
                raise ValueError(f"ExplanationResponseV1 validation failed: metadata key '{key}' is missing.")
