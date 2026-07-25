"""Interface contract definition for Timeline compiler services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.timeline_event import TimelineEvent

class ITimelineBuilder(ABC):
    """Abstract contract mapping pipeline evaluation events into chronological steps."""

    @abstractmethod
    def build_timeline(self, hybrid_result: HybridRiskResult, metadata: Dict[str, Any]) -> List[TimelineEvent]:
        """Compiles chronological audit sequences for the investigation dashboard.

        Args:
            hybrid_result: Unified assessment risk profile.
            metadata: Pipeline execution parameters.

        Returns:
            List[TimelineEvent]: Sequence events listing.
        """
        pass
