"""Explanation builder implementation converting evidence items to structured JSON maps."""

from typing import Any, Dict, Optional
from app.explainability.interfaces.i_explanation_builder import IExplanationBuilder
from app.explainability.interfaces.i_explanation_policy import IExplanationPolicy
from app.explainability.policies.deterministic_explanation_policy import DeterministicExplanationPolicy
from app.models.explainability_context import ExplainabilityContext

class ExplanationBuilder(IExplanationBuilder):
    """Organizes score breakdown metrics and evidence ledgers into serializable dictionary mappings."""

    def __init__(self, policy: Optional[IExplanationPolicy] = None):
        """Initializes ExplanationBuilder.

        Args:
            policy: Custom policy logic. Default: DeterministicExplanationPolicy.
        """
        self.policy = policy or DeterministicExplanationPolicy()

    def build(self, context: ExplainabilityContext) -> Dict[str, Any]:
        """Arranges metrics into a structured dictionary mapping.

        Args:
            context: Consolidated explainability call context.

        Returns:
            Dict[str, Any]: Structured dictionary report.
        """
        res = context.hybrid_result
        bundle = context.evidence_bundle

        # Order and filter evidence based on policy
        all_evidence = bundle.rule_evidence + bundle.ml_evidence + bundle.behavioral_evidence
        filtered = self.policy.filter_evidence(all_evidence)
        ordered = self.policy.order_evidence(filtered)
        redacted = self.policy.redact_evidence(ordered)

        limit = self.policy.get_formatting_options().get("limit_count", 5)
        top_factors = redacted[:limit]

        # Build structured JSON explanation
        explanation_map = {
            "Overall Risk": res.severity,
            "Risk Score": res.overall_risk_score,
            "Severity": res.severity,
            "Confidence": res.confidence,
            "Top Risk Factors": [
                {
                    "factor": item.title,
                    "severity": item.severity,
                    "contribution_score": item.score,
                    "trace_id": item.rule_id or item.anomaly_id
                } for item in top_factors
            ],
            "Triggered Rules": res.triggered_rules,
            "Behavioral Findings": {
                item.title: item.score for item in redacted if item.source == "BEHAVIORAL"
            },
            "ML Findings": {
                "outlier_score": res.anomaly_score,
                "is_outlier": res.anomaly_score >= 0.5
            },
            "Recommendation": res.recommendation,
            "policy_depth": self.policy.get_depth()
        }

        return explanation_map
