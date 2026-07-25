"""Rule check class for validating round transaction amounts."""

import pandas as pd
from app.config.rule_thresholds import ROUND_AMOUNT_SCORE, ROUND_AMOUNT_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class RoundAmountRule(BaseRule):
    """Flags high percentages of transactions occurring in exact round numbers."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_ROUND_AMOUNT",
            rule_name="Round Amount",
            description="Customer executed high ratio of round-number transactions.",
            threshold=ROUND_AMOUNT_THRESHOLD,
            score=ROUND_AMOUNT_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("round_amount_ratio", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"round_amount_ratio": val, "threshold": self.threshold}
        )
