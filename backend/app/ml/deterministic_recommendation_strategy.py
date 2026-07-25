"""Deterministic recommendation strategy matching fused scores to threshold levels."""

from typing import Any, List
from app.config import ml_config
from app.ml.interfaces.recommendation_engine import IRecommendationStrategy

class DeterministicRecommendationStrategy(IRecommendationStrategy):
    """Checks overall score against configurable boundary thresholds to output actions."""

    def __init__(self, rules: List[dict] = None):
        """Initializes the recommendation strategy.

        Args:
            rules: Optional list of recommendation rule dicts.
        """
        self.rules = rules if rules is not None else getattr(
            ml_config, "HYBRID_RECOMMENDATION_RULES", []
        )
        # Sort rules in descending order of min_score to evaluate higher thresholds first
        self.rules = sorted(self.rules, key=lambda x: x.get("min_score", 0.0), reverse=True)

    def determine_recommendation(self, overall_score: float) -> str:
        """Determines recommendation based on score.

        Args:
            overall_score: Unified hybrid risk score (0.0 to 1.0)

        Returns:
            str: Recommendation action.
        """
        for rule in self.rules:
            min_score = rule.get("min_score", 0.0)
            if overall_score >= min_score:
                return rule.get("recommendation", "Continue Monitoring")
        return "Continue Monitoring"
