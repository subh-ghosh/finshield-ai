"""Rule check class for validating transaction structuring."""

import pandas as pd
from app.config.rule_thresholds import STRUCTURING_SCORE, STRUCTURING_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class StructuringRule(BaseRule):
    """Flags potential structuring where transactions are split to avoid limits."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_STRUCTURING",
            rule_name="Structuring",
            description="Customer executed structured transactions below reporting limits.",
            threshold=STRUCTURING_THRESHOLD,
            score=STRUCTURING_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("structuring_score", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"structuring_score": val, "threshold": self.threshold}
        )
