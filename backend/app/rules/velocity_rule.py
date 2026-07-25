"""Rule check class for validating transaction velocity."""

import pandas as pd
from app.config.rule_thresholds import HIGH_VELOCITY_SCORE, HIGH_VELOCITY_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class VelocityRule(BaseRule):
    """Flags customers executing transaction volumes at a suspicious velocity."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_VELOCITY",
            rule_name="High Velocity",
            description="Customer executed unusually high transaction velocity.",
            threshold=HIGH_VELOCITY_THRESHOLD,
            score=HIGH_VELOCITY_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("velocity_score", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"velocity_score": val, "threshold": self.threshold}
        )
