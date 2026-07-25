"""Rule check class for validating large transaction amounts."""

import pandas as pd
from app.config.rule_thresholds import LARGE_TRANSACTION_SCORE, LARGE_TRANSACTION_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class LargeTransactionRule(BaseRule):
    """Flags single transaction amounts exceeding established limits."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_LARGE_TRANSACTION",
            rule_name="Large Transaction",
            description="Customer executed transaction exceeding standard thresholds.",
            threshold=LARGE_TRANSACTION_THRESHOLD,
            score=LARGE_TRANSACTION_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("maximum_amount", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"maximum_amount": val, "threshold": self.threshold}
        )
