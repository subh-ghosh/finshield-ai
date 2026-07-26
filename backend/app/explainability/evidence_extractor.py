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
        """Parses component scores and risk factors into a structured bundle."""
        pass  # Legacy method

    def explain_evidence_graph(self, evidence_graph: dict) -> str:
        """Consumes the structured evidence graph from the multi-agent system
        and generates a natural language explanation."""
        
        attribution = evidence_graph.get("attribution", {})
        layers = evidence_graph.get("layers", [])
        
        explanation_parts = []
        explanation_parts.append("Risk Attribution Summary:")
        
        # Build explanation from attribution percentages
        if attribution.get("rule_pct", 0) > 0:
            explanation_parts.append(f"- {attribution['rule_pct']}% of the risk came from the Rule Intelligence Agent.")
        if attribution.get("ml_pct", 0) > 0:
            explanation_parts.append(f"- {attribution['ml_pct']}% of the risk came from the ML Intelligence Agent.")
        if attribution.get("graph_pct", 0) > 0:
            explanation_parts.append(f"- {attribution['graph_pct']}% of the risk came from the Network Agent.")
        if attribution.get("compliance_pct", 0) > 0:
            explanation_parts.append(f"- {attribution['compliance_pct']}% of the risk came from the Compliance Agent.")
            
        explanation_parts.append("\nDetailed Findings:")
        for layer in layers:
            if layer["count"] > 0:
                explanation_parts.append(f"\n[{layer['name']} ({layer['count']} items)]")
                for item in layer["items"]:
                    desc = item.get("description", "No description provided.")
                    explanation_parts.append(f"  * {desc}")
                    
        return "\n".join(explanation_parts)
