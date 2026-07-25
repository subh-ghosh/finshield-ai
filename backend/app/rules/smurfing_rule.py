"""Rule check class for validating smurfing activity."""

import pandas as pd
from app.config.rule_thresholds import SMURFING_SCORE, SMURFING_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class SmurfingRule(BaseRule):
    """Flags suspected smurfing patterns involving multiple related accounts."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_SMURFING",
            rule_name="Smurfing",
            description="Customer initiated multi-source account smurfing activity.",
            threshold=SMURFING_THRESHOLD,
            score=SMURFING_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("smurfing_score", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"smurfing_score": val, "threshold": self.threshold}
        )
