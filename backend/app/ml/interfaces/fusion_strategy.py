"""Fusion strategy abstract interface contract definition."""

from abc import ABC, abstractmethod
from typing import Dict

class IFusionStrategy(ABC):
    """Interface defining the capability to fuse multiple risk components into a single overall score."""

    @abstractmethod
    def fuse(self, rule_score: float, ml_score: float, behavioral_score: float) -> float:
        """Fuses multiple threat scores.

        Args:
            rule_score: Normalized Rule Engine score.
            ml_score: Outlier prediction anomaly score.
            behavioral_score: Normalized behavioral risk score.

        Returns:
            float: Unified overall score (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def get_weights(self) -> Dict[str, float]:
        """Returns the configuration weights active in this strategy.

        Returns:
            Dict[str, float]: Dictionary of component weights.
        """
        pass
