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
