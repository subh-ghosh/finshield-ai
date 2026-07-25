"""Recommendation engine implementing IRecommendationEngine using strategy injection."""

from typing import Optional
from app.ml.interfaces.recommendation_engine import IRecommendationEngine, IRecommendationStrategy
from app.ml.deterministic_recommendation_strategy import DeterministicRecommendationStrategy

class RecommendationEngine(IRecommendationEngine):
    """Generates case dispositions by delegating to an injected IRecommendationStrategy."""

    def __init__(self, strategy: Optional[IRecommendationStrategy] = None):
        """Initializes the recommendation engine.

        Args:
            strategy: Custom strategy implementation. Default: DeterministicRecommendationStrategy.
        """
        self.strategy = strategy or DeterministicRecommendationStrategy()

    def generate(self, overall_score: float) -> str:
        """Invokes the strategy to compute matching case action recommendation.

        Args:
            overall_score: Consolidated overall risk score.

        Returns:
            str: Recommended action.
        """
        return self.strategy.determine_recommendation(overall_score)
