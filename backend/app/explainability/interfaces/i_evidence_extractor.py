"""Interface contract definition for Evidence Extraction services."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.evidence_bundle import EvidenceBundle

class IEvidenceExtractor(ABC):
    """Abstract contract responsible for parsing components output into a unified EvidenceBundle."""

    @abstractmethod
    def extract(self, hybrid_result: HybridRiskResult, raw_features: Dict[str, Any]) -> EvidenceBundle:
        """Parses the rule list, isolation forest alerts, and behavioral metrics.

        Args:
            hybrid_result: Consolidated risk profile result.
            raw_features: Dictionary representing raw customer features.

        Returns:
            EvidenceBundle: Unranked evidence bundle.
        """
        pass
