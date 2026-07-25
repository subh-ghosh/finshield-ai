"""Deterministic explanation policy configuration implementation."""

from typing import Any, Dict, List
from app.ml.interfaces.recommendation_engine import IRecommendationStrategy  # Or just import interfaces
from app.explainability.interfaces.i_explanation_policy import IExplanationPolicy
from app.models.evidence_item import EvidenceItem

class DeterministicExplanationPolicy(IExplanationPolicy):
    """Simple default policy that formats detailed, sorted evidence without redactions."""

    def __init__(self, depth: str = "detailed", options: Dict[str, Any] = None):
        """Initializes DeterministicExplanationPolicy.

        Args:
            depth: Target depth detail level.
            options: Custom flags dictionary.
        """
        self.depth = depth
        self.options = options or {"limit_count": 10, "markdown_enabled": True}

    def get_depth(self) -> str:
        """Returns details depth tier."""
        return self.depth

    def filter_evidence(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Applies filters to restrict evidence listings (returns all elements by default)."""
        return evidence

    def order_evidence(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Sorts evidence list descending by score."""
        return sorted(evidence, key=lambda x: x.score, reverse=True)

    def redact_evidence(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Performs no redactions (returns elements unmodified)."""
        return evidence

    def get_formatting_options(self) -> Dict[str, Any]:
        """Returns visual formatting flags."""
        return self.options
