"""Markdown output format serializer implementation formatting reports in GitHub-flavored markdown."""

from app.explainability.interfaces.i_output_serializer import IOutputSerializer
from app.models.explanation_response import ExplanationResponseV1

class MarkdownSerializer(IOutputSerializer):
    """Formats ExplanationResponseV1 reports in beautiful Markdown text structures."""

    def serialize(self, response: ExplanationResponseV1) -> str:
        """Transforms response to markdown format.

        Args:
            response: Consolidated ExplanationResponseV1.

        Returns:
            str: Compiled markdown string.
        """
        md_lines = [
            f"# Investigator Risk Explanation Report: {response.customer_id}",
            f"**Overall Risk Score:** `{response.overall_risk_score:.4f}`",
            f"**Severity Level:** `{response.severity}`",
            f"**Confidence Level:** `{response.confidence * 100:.1f}%`",
            "",
            "## Case Executive Summary",
            response.summary,
            "",
            "## Compliance Recommendation",
            f"> [!IMPORTANT]",
            f"> **Recommended Case Action:** {response.recommendation}",
            "",
            "## Score Breakdown",
            f"- **Rule Engine normalized score:** `{response.risk_breakdown.get('rule_score', 0.0):.4f}`",
            f"- **Isolation Forest outlier score:** `{response.risk_breakdown.get('ml_score', 0.0):.4f}`",
            f"- **Behavioral analyzer risk score:** `{response.risk_breakdown.get('behavioral_score', 0.0):.4f}`",
            "",
            "## Case Evidence Ledger",
        ]
        
        for idx, item in enumerate(response.evidence, 1):
            md_lines.append(f"### {idx}. {item.title} ({item.source})")
            md_lines.append(f"- **Severity:** `{item.severity}` | **Contribution Score:** `{item.score:.4f}`")
            md_lines.append(f"- **Details:** {item.description}")
            if item.rule_id:
                md_lines.append(f"- **Origin Trace ID:** `{item.rule_id}`")
            elif item.anomaly_id:
                md_lines.append(f"- **Origin Trace ID:** `{item.anomaly_id}`")
            md_lines.append("")

        md_lines.append("## Chronological Investigation Timeline")
        for event in response.timeline:
            md_lines.append(f"- `[{event.source}]` {event.event_name} (Severity: `{event.severity}`) - {event.description}")

        md_lines.append("")
        md_lines.append("---")
        md_lines.append(f"*Generated at `{response.metadata.get('generated_at', '')}` by `{response.metadata.get('generator', {}).get('service_name', 'ExplainabilityService')}`.*")
        
        return "\n".join(md_lines)

    def get_format_name(self) -> str:
        """Returns format name identifier."""
        return "markdown"
