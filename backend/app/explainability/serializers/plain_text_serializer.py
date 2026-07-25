"""Plain text output format serializer implementation returning ascii reports."""

from app.explainability.interfaces.i_output_serializer import IOutputSerializer
from app.models.explanation_response import ExplanationResponseV1

class PlainTextSerializer(IOutputSerializer):
    """Formats ExplanationResponseV1 reports in clean Plain Text structure."""

    def serialize(self, response: ExplanationResponseV1) -> str:
        """Transforms response to plain text format.

        Args:
            response: Consolidated ExplanationResponseV1.

        Returns:
            str: Compiled plain text report.
        """
        lines = [
            f"INVESTIGATOR RISK EXPLANATION REPORT: {response.customer_id}",
            "=" * 50,
            f"Overall Risk Score: {response.overall_risk_score:.4f}",
            f"Severity Level: {response.severity}",
            f"Confidence Level: {response.confidence * 100:.1f}%",
            "",
            "CASE EXECUTIVE SUMMARY:",
            response.summary,
            "",
            f"RECOMMENDED COMPLIANCE ACTION: {response.recommendation}",
            "",
            "SCORE BREAKDOWN:",
            f"  - Rule Engine Score: {response.risk_breakdown.get('rule_score', 0.0):.4f}",
            f"  - Isolation Forest Score: {response.risk_breakdown.get('ml_score', 0.0):.4f}",
            f"  - Behavioral Score: {response.risk_breakdown.get('behavioral_score', 0.0):.4f}",
            "",
            "CASE EVIDENCE LEDGER:",
        ]
        
        for idx, item in enumerate(response.evidence, 1):
            lines.append(f"  {idx}. {item.title} [{item.source}]")
            lines.append(f"     Severity: {item.severity} | Score Contribution: {item.score:.4f}")
            lines.append(f"     Details: {item.description}")
            if item.rule_id:
                lines.append(f"     Origin: Rule ID {item.rule_id}")
            elif item.anomaly_id:
                lines.append(f"     Origin: Anomaly ID {item.anomaly_id}")
            lines.append("")

        lines.append("CHRONOLOGICAL TIMELINE:")
        for event in response.timeline:
            lines.append(f"  - [{event.source}] {event.event_name}: {event.description} (Severity: {event.severity})")

        return "\n".join(lines)

    def get_format_name(self) -> str:
        """Returns format name identifier."""
        return "text"
