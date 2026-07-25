"""Rule check class for validating recipient diversity."""

import pandas as pd
from app.config.rule_thresholds import RECIPIENT_DIVERSITY_SCORE, RECIPIENT_DIVERSITY_THRESHOLD
from app.models.rule_evaluation import RuleEvaluation
from app.rules.base_rule import BaseRule

class RecipientDiversityRule(BaseRule):
    """Flags customers sending funds to a high number of unique counterparties."""

    def __init__(self):
        super().__init__(
            rule_id="RULE_RECIPIENT_DIVERSITY",
            rule_name="Recipient Diversity",
            description="Customer sent transactions to a high diversity of recipients.",
            threshold=RECIPIENT_DIVERSITY_THRESHOLD,
            score=RECIPIENT_DIVERSITY_SCORE
        )

    def evaluate(self, customer: pd.Series) -> RuleEvaluation:
        val = float(customer.get("recipient_diversity", 0.0))
        triggered = val > self.threshold
        return RuleEvaluation(
            triggered=triggered,
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            score=self.score,
            severity=self._get_severity(),
            explanation=self.description,
            evidence={"recipient_diversity": val, "threshold": self.threshold}
        )
