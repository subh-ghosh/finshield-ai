"""Explainability context representing parameters passed to explainability generation services."""

from dataclasses import dataclass, field
from typing import Any, Dict
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.evidence_bundle import EvidenceBundle

@dataclass
class ExplainabilityContext:
    """Holds input risk profiles, configurations, bundles, and metadata for explainability runs."""
    hybrid_result: HybridRiskResult
    evidence_bundle: EvidenceBundle
    pipeline_metadata: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    generation_options: Dict[str, Any] = field(default_factory=dict)
