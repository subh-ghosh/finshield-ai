"""Interface contract definition for Explanation Policies."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from app.models.evidence_item import EvidenceItem

class IExplanationPolicy(ABC):
    """Abstract contract managing explanation detail, sorting, filtering, and data redactions."""

    @abstractmethod
    def get_depth(self) -> str:
        """Returns details depth tier (e.g. 'brief', 'detailed', 'verbose')."""
        pass

    @abstractmethod
    def filter_evidence(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Applies filters to restrict evidence listings.

        Args:
            evidence: Complete list of evidence.

        Returns:
            List[EvidenceItem]: Filtered list of evidence.
        """
        pass

    @abstractmethod
    def order_evidence(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Arranges evidence in order of relevance.

        Args:
            evidence: Evidence items.

        Returns:
            List[EvidenceItem]: Ordered list of evidence.
        """
        pass

    @abstractmethod
    def redact_evidence(self, evidence: List[EvidenceItem]) -> List[EvidenceItem]:
        """Redacts sensitive values or customer names if needed.

        Args:
            evidence: Evidence items.

        Returns:
            List[EvidenceItem]: Redacted list of evidence.
        """
        pass

    @abstractmethod
    def get_formatting_options(self) -> Dict[str, Any]:
        """Returns visual formatting rule flags (e.g. HTML enabled, limit count)."""
        pass
