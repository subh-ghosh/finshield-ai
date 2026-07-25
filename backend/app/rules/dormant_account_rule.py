"""Rule check class for validating dormant account reactivation."""

import pandas as pd
from app.config.rule_thresholds import DORMANT_ACCOUNT_SCORE, DORMANT_ACCOUNT_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class DormantAccountRule(BaseRule):
    """Flags sudden significant activity on accounts that were long dormant."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_DORMANT_ACCOUNT",
            rule_name="Dormant Account",
            description="Customer transacted after a prolonged period of inactivity.",
            threshold=DORMANT_ACCOUNT_THRESHOLD,
            score=DORMANT_ACCOUNT_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("days_since_last_transaction", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"days_since_last_transaction": val, "threshold": self.threshold}
        )
