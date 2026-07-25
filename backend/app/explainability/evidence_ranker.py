"""Evidence ranker implementation sorting and deduplicating list of EvidenceItems."""

from typing import Dict, List
from app.explainability.interfaces.i_evidence_ranker import IEvidenceRanker
from app.models.evidence_bundle import EvidenceBundle
from app.models.evidence_item import EvidenceItem

class EvidenceRanker(IEvidenceRanker):
    """Sorts evidence list by severity rank and score values, eliminating redundant duplicates."""

    def __init__(self):
        """Initializes EvidenceRanker."""
        self.severity_order = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3
        }

    def rank(self, bundle: EvidenceBundle) -> EvidenceBundle:
        """Deduplicates and sorts evidence lists.

        Args:
            bundle: Unranked input evidence bundle.

        Returns:
            EvidenceBundle: Ranked and filtered evidence bundle.
        """
        ranked_rules = self._rank_list(bundle.rule_evidence)
        ranked_ml = self._rank_list(bundle.ml_evidence)
        ranked_beh = self._rank_list(bundle.behavioral_evidence)

        return EvidenceBundle(
            rule_evidence=ranked_rules,
            ml_evidence=ranked_ml,
            behavioral_evidence=ranked_beh,
            metadata={**bundle.metadata, "ranked": True}
        )

    def _rank_list(self, items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Deduplicates and sorts a single list of EvidenceItem elements."""
        if not items:
            return []

        # Deduplicate: Keep item with highest score if name and source are identical
        dedup_map: Dict[str, EvidenceItem] = {}
        for item in items:
            key = f"{item.source}:{item.title}"
            existing = dedup_map.get(key)
            if existing is None or item.score > existing.score:
                dedup_map[key] = item

        # Sort: severity first (ascending in order index), then score (descending)
        unique_items = list(dedup_map.values())
        unique_items.sort(key=lambda x: (self.severity_order.get(x.severity, 4), -x.score))
        return unique_items
