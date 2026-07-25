"""Base abstract class for all deterministic AML rule check definitions."""

from abc import ABC, abstractmethod
import pandas as pd
from app.models.rule_evaluation import RuleEvaluation

class BaseRule(ABC):
    """Abstract base class establishing the attributes and interfaces for AML rules."""

    def __init__(self, rule_id: str, rule_name: str, description: str, threshold: float, score: int):
        """Initializes rule attributes.

        Args:
            rule_id: Unique string identifier for the rule.
            rule_name: Human-readable name.
            description: Concise description of the business case.
            threshold: Numeric condition threshold value.
            score: Risk score points contributed if triggered.
        """
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.description = description
        self.threshold = threshold
        self.score = score

    @abstractmethod
    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        """Evaluates a single customer record against the rule check condition.

        Args:
            customer: Pandas Series containing the engineered customer features.

        Returns:
            RuleEvaluation: Results of the evaluation.
        """
        pass

    def _get_severity(self) -> str:
        """Resolves rule-level severity based on score brackets."""
        if self.score >= 70:
            return "CRITICAL"
        elif self.score >= 40:
            return "HIGH"
        elif self.score >= 20:
            return "MEDIUM"
        return "LOW"
