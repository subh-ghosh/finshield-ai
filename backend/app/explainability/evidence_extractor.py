"""Evidence extractor implementation parsing risk elements into structured evidence lists."""

import time
from typing import Any, Dict, List
from app.explainability.interfaces.i_evidence_extractor import IEvidenceExtractor
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.evidence_bundle import EvidenceBundle
from app.models.evidence_item import EvidenceItem


class EvidenceExtractor(IEvidenceExtractor):
    """Traverses hybrid evaluation risk factors to compile unranked categories of EvidenceItems."""

    def extract(self, hybrid_result: HybridRiskResult, raw_features: Dict[str, Any]) -> EvidenceBundle:
        """Parses component scores and risk factors into a structured bundle.

        Args:
            hybrid_result: Consolidated risk profile result.
            raw_features: Dictionary representing customer features.

        Returns:
            EvidenceBundle: Unranked evidence bundle.
        """
        rule_evidence: List[EvidenceItem] = []
        ml_evidence: List[EvidenceItem] = []
        behavioral_evidence: List[EvidenceItem] = []

        now = time.time()

        for factor in hybrid_result.risk_factors:
            source = factor.source

            # Resolve traceability codes
            rule_id = None
            anomaly_id = None
            feature_name = None

            if source == "RULE_ENGINE":
                rule_id = factor.name.replace("RULE_", "")
            elif source == "ISOLATION_FOREST":
                anomaly_id = "ISOLATION_FOREST_OUTLIER"
            elif source == "BEHAVIORAL":
                feature_name = factor.name.replace("BEHAVIORAL_", "").lower()

            item = EvidenceItem(
                source=source,
                title=factor.name,
                description=factor.description,
                severity=factor.severity,
                score=factor.score,
                confidence=hybrid_result.confidence,
                rule_id=rule_id,
                anomaly_id=anomaly_id,
                feature_name=feature_name,
                pipeline_stage=source,
                timestamp=now,
                metadata={"raw_value": raw_features.get(feature_name) if feature_name else None}
            )

            if source == "RULE_ENGINE":
                rule_evidence.append(item)
            elif source == "ISOLATION_FOREST":
                ml_evidence.append(item)
            elif source == "BEHAVIORAL":
                behavioral_evidence.append(item)

        # Fallback if Isolation Forest predicted normal but score is populated
        if not ml_evidence and hybrid_result.anomaly_score > 0.0:
            ml_evidence.append(
                EvidenceItem(
                    source="ISOLATION_FOREST",
                    title="ML_OUTLIER_IFOREST_BASELINE",
                    description=f"Isolation Forest calculated anomaly score of {hybrid_result.anomaly_score:.4f}",
                    severity="LOW" if hybrid_result.anomaly_score < 0.5 else "HIGH",
                    score=hybrid_result.anomaly_score,
                    confidence=hybrid_result.confidence,
                    anomaly_id="ISOLATION_FOREST_OUTLIER",
                    pipeline_stage="ISOLATION_FOREST",
                    timestamp=now
                )
            )

        return EvidenceBundle(
            rule_evidence=rule_evidence,
            ml_evidence=ml_evidence,
            behavioral_evidence=behavioral_evidence,
            metadata={"extracted_at": now}
        )

    def explain_evidence_graph(self, evidence_graph: dict) -> str:
        """Consumes the structured evidence graph from the V2 multi-agent system
        and generates a natural language explanation for regulators and analysts.

        This is the V2 upgrade. The legacy ``extract()`` method above feeds the
        classic explainability pipeline. This method feeds the new agent-based
        pipeline, where the evidence graph has already been categorised by agent.

        Args:
            evidence_graph: Dict with ``layers`` and ``attribution`` keys,
                as produced by ``evidence_aggregator`` in ``agent/graph.py``.

        Returns:
            str: Human-readable attribution summary.
        """
        attribution = evidence_graph.get("attribution", {})
        layers = evidence_graph.get("layers", [])

        parts = ["## V2 Risk Attribution Summary\n"]

        # Attribution bar summary
        if attribution.get("rule_pct", 0) > 0:
            parts.append(f"- **{attribution['rule_pct']}%** of the risk signal came from the **Rule Intelligence Agent** "
                         f"(deterministic AML threshold rules).")
        if attribution.get("ml_pct", 0) > 0:
            parts.append(f"- **{attribution['ml_pct']}%** came from the **ML Intelligence Agent** "
                         f"(Isolation Forest anomaly detection).")
        if attribution.get("graph_pct", 0) > 0:
            parts.append(f"- **{attribution['graph_pct']}%** came from the **Network Agent** "
                         f"(counterparty graph analysis).")
        if attribution.get("compliance_pct", 0) > 0:
            parts.append(f"- **{attribution['compliance_pct']}%** came from the **Compliance Agent** "
                         f"(hybrid risk fusion).")

        parts.append("\n### Detailed Findings by Agent\n")
        for layer in layers:
            if layer.get("count", 0) > 0:
                parts.append(f"\n**{layer['name']}** ({layer['count']} item(s))")
                for item in layer.get("items", []):
                    desc = item.get("description", "No description provided.")
                    parts.append(f"  * {desc}")

        return "\n".join(parts)
