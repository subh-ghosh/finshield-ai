"""Rule check class for validating rapid cash outs."""

import pandas as pd
from app.config.rule_thresholds import HIGH_CASHOUT_SCORE, HIGH_CASHOUT_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class RapidCashOutRule(BaseRule):
    """Flags accounts transferring funds out rapidly after accumulation."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_RAPID_CASHOUT",
            rule_name="Rapid Cash Out",
            description="Customer cash-out ratio exceeds risk thresholds.",
            threshold=HIGH_CASHOUT_THRESHOLD,
            score=HIGH_CASHOUT_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("cash_out_ratio", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"cash_out_ratio": val, "threshold": self.threshold}
        )
