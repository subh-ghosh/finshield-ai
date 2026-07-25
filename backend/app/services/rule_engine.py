"""Rule engine service orchestrating evaluations and alert compilations."""

from typing import List
import pandas as pd
from app.models.analysis_result import AnalysisResult
from app.models.rule_evaluation import RuleEvaluation
from app.models.triggered_rule import TriggeredRule
from app.rules.dormant_account_rule import DormantAccountRule
from app.rules.large_transaction_rule import LargeTransactionRule
from app.rules.rapid_cashout_rule import RapidCashOutRule
from app.rules.recipient_diversity_rule import RecipientDiversityRule
from app.rules.round_amount_rule import RoundAmountRule
from app.rules.smurfing_rule import SmurfingRule
from app.rules.structuring_rule import StructuringRule
from app.rules.velocity_rule import VelocityRule
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RuleEngine:
    """Executes registered AML rules and groups results into customer AnalysisResult alerts."""

    def __init__(self):
        """Initializes the RuleEngine and registers default rules."""
        self.rules = [
            VelocityRule(),
            StructuringRule(),
            SmurfingRule(),
            RoundAmountRule(),
            RapidCashOutRule(),
            RecipientDiversityRule(),
            DormantAccountRule(),
            LargeTransactionRule()
        ]
        logger.info(f"Rule Engine Started - Rules Registered: {len(self.rules)}")

    def run(self, customer_features: pd.DataFrame) -> List[AnalysisResult]:
        """Runs the rule engine on the customer features matrix.

        Args:
            customer_features: Customer features DataFrame.

        Returns:
            List[AnalysisResult]: Structured analysis results.
        """
        logger.info("Rule Engine started evaluation...")
        analysis_results: List[AnalysisResult] = []
        customers_processed = len(customer_features)
        customers_flagged = 0
        total_accumulated_score = 0

        for _, row in customer_features.iterrows():
            customer_id = str(row["customer_id"])
            triggered_rules: List[TriggeredRule] = []
            total_score = 0

            for rule in self.rules:
                eval_res: RuleEvaluation = rule.evaluate(row)
                if eval_res.triggered:
                    triggered_rules.append(
                        TriggeredRule(
                            rule_id=eval_res.rule_id,
                            rule_name=eval_res.rule_name,
                            score=eval_res.score,
                            severity=eval_res.severity,
                            description=rule.description,
                            explanation=eval_res.explanation,
                            evidence=eval_res.evidence
                        )
                    )
                    total_score += eval_res.score

            severity = self._classify_severity(total_score)
            if total_score > 0:
                customers_flagged += 1
            total_accumulated_score += total_score

            analysis_results.append(
                AnalysisResult(
                    customer_id=customer_id,
                    total_rule_score=total_score,
                    severity=severity,
                    triggered_rules=triggered_rules
                )
            )

        avg_score = (total_accumulated_score / customers_processed) if customers_processed > 0 else 0.0

        logger.info("==========================================")
        logger.info("         RULE ENGINE SUMMARY              ")
        logger.info("==========================================")
        logger.info(f"Rules Registered    : {len(self.rules)}")
        logger.info(f"Customers Processed : {customers_processed}")
        logger.info(f"Customers Flagged   : {customers_flagged}")
        logger.info(f"Average Rule Score  : {avg_score:.2f}")
        logger.info("Rule Engine Completed")
        logger.info("==========================================")

        return analysis_results

    @staticmethod
    def to_dataframe(analysis_results: List[AnalysisResult]) -> pd.DataFrame:
        """Converts a list of AnalysisResult objects to a Pandas DataFrame.

        Args:
            analysis_results: List of AnalysisResult objects.

        Returns:
            pd.DataFrame: DataFrame containing rule evaluation columns.
        """
        rows = []
        for res in analysis_results:
            triggered = [r.rule_id for r in res.triggered_rules]
            explanations = [r.explanation for r in res.triggered_rules]
            evidence = [r.evidence for r in res.triggered_rules]

            rows.append({
                "customer_id": res.customer_id,
                "rule_score": res.total_rule_score,
                "severity": res.severity,
                "triggered_rules": triggered,
                "rule_explanations": explanations,
                "rule_evidence": evidence
            })

        return pd.DataFrame(rows)

    @staticmethod
    def _classify_severity(score: int) -> str:
        """Helper to map total score into severity classifications."""
        if score >= 70:
            return "CRITICAL"
        elif score >= 40:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        return "LOW"
