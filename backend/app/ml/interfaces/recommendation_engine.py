"""Recommendation strategy and engine abstract interface contracts definition."""

from abc import ABC, abstractmethod

class IRecommendationStrategy(ABC):
    """Interface defining decision rules algorithms matching overall scores to recommendations."""

    @abstractmethod
    def determine_recommendation(self, overall_score: float) -> str:
        """Determines recommendation based on score.

        Args:
            overall_score: Consolidated overall risk score.

        Returns:
            str: Deterministic recommendation action.
        """
        pass


class IRecommendationEngine(ABC):
    """Interface defining the engine capable of generating case disposition recommendations."""

    @abstractmethod
    def generate(self, overall_score: float) -> str:
        """Generates case action recommendation.

        Args:
            overall_score: Fused overall risk score.

        Returns:
            str: Recommendation action.
        """
        pass
