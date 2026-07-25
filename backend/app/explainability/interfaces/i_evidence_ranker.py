"""Interface contract definition for Evidence Ranking and sorting services."""

from abc import ABC, abstractmethod
from app.models.evidence_bundle import EvidenceBundle

class IEvidenceRanker(ABC):
    """Abstract contract responsible for filtering, sorting, and deduplicating evidence items."""

    @abstractmethod
    def rank(self, bundle: EvidenceBundle) -> EvidenceBundle:
        """Ranks evidence list based on severity, confidence, or scoring weights.

        Args:
            bundle: Unranked input evidence bundle.

        Returns:
            EvidenceBundle: Sorted and ranked evidence bundle.
        """
        pass
