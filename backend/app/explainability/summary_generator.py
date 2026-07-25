"""Summary generator implementation using config-driven explanation templates."""

from typing import Dict
from app.config import explainability_config
from app.explainability.interfaces.i_summary_generator import ISummaryGenerator
from app.models.explainability_context import ExplainabilityContext
from app.models.investigation_summary import InvestigationSummary

class SummaryGenerator(ISummaryGenerator):
    """Interpolates config templates to generate deterministic natural-language investigator reports."""

    def __init__(self, templates: Dict[str, Dict[str, str]] = None):
        """Initializes SummaryGenerator.

        Args:
            templates: Custom template dictionary to override config.
        """
        self.templates = templates if templates is not None else getattr(
            explainability_config, "EXPLANATION_TEMPLATES", {}
        )

    def generate_summary(self, context: ExplainabilityContext) -> InvestigationSummary:
        """Interpolates templates based on context risk values.

        Args:
            context: Consolidated explainability call context.

        Returns:
            InvestigationSummary: Written summary.
        """
        res = context.hybrid_result
        severity = res.severity.upper()
        
        # Safe lookup in configured templates
        tmpl = self.templates.get(severity, self.templates.get("LOW", {}))
        summary_str = tmpl.get("summary", "")
        findings_str = tmpl.get("findings", "")

        # Format rules list
        rules_triggered = res.triggered_rules
        rules_list_str = ", ".join(rules_triggered) if rules_triggered else "None"
        rules_summary_str = (
            f"{len(rules_triggered)} rules violated ({rules_list_str})"
            if rules_triggered else "no rule violations"
        )

        # Format behavioral features list
        bundle = context.evidence_bundle
        beh_names = [e.title.replace("BEHAVIORAL_", "").lower() for e in bundle.behavioral_evidence]
        beh_summary_str = ", ".join(beh_names) if beh_names else "none"

        # Format ML status
        ml_summary_str = "Outlier state detected" if res.anomaly_score >= 0.5 else "Within normal outlier bounds"

        # Interpolate variables safely
        narrative = summary_str.format(
            customer_id=res.customer_id,
            rules_summary=rules_summary_str,
            behavior_summary=beh_summary_str,
            ml_summary=ml_summary_str,
            ml_score=res.anomaly_score
        )

        score_interpretation = findings_str.format(
            rules_list=rules_list_str,
            ml_score=res.anomaly_score
        )

        conclusion = f"Action Item: {res.recommendation}. Fused threat index is {res.overall_risk_score:.4f}."

        return InvestigationSummary(
            narrative=narrative,
            score_interpretation=score_interpretation,
            conclusion=conclusion
        )
