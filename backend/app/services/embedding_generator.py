"""Dual Vector Embedding Generator for Enterprise Investigation Memory Store.

Generates both:
1. Structured Feature Vector (16-dimensional dense numerical array)
2. Semantic Text Embedding Vector (32-dimensional dense text array)
"""

import math
import numpy as np
from typing import List, Dict, Any
from app.models.investigation_memory import MemoryFeatureVector, StoreMemoryRequest


class MemoryEmbeddingGenerator:
    """Generates deterministic dual vectors (structured numerical & semantic text)."""

    def generate_feature_vector(self, req: StoreMemoryRequest) -> MemoryFeatureVector:
        """Constructs a normalized 16-dimensional structured feature vector."""
        r_score = float(req.risk_score) / 100.0
        rule_s = min(1.0, len(req.triggered_rules) * 0.25)
        ml_s = float(req.isolation_forest_score)
        struct_s = float(req.behavioral_features.get("structuring_indicator", 0.0))
        vel_s = float(req.behavioral_features.get("velocity_multiplier", 1.0)) / 5.0
        cash_r = float(req.behavioral_features.get("cash_ratio", 0.0))
        cb_r = float(req.behavioral_features.get("cross_border_ratio", 0.0))
        compl_s = float(req.compliance_completeness_score) / 100.0

        # Decision encoding: CLEAR=0.1, MANUAL_REVIEW=0.4, ESCALATE=0.7, FILE_SAR=1.0
        dec_map = {"CLEAR": 0.1, "MANUAL_REVIEW": 0.4, "ESCALATE": 0.7, "FILE_SAR": 1.0}
        dec_enc = dec_map.get(req.final_decision.upper(), 0.5)

        # Jurisdiction encoding
        jur_hash = (abs(hash(req.jurisdiction)) % 100) / 100.0
        ind_hash = (abs(hash(req.industry)) % 100) / 100.0

        dense = [
            r_score,
            rule_s,
            ml_s,
            struct_s,
            vel_s,
            cash_r,
            cb_r,
            compl_s,
            dec_enc,
            jur_hash,
            ind_hash,
            1.0 if req.sar_narrative else 0.0,
            float(req.network_metrics.get("degree", 1)) / 10.0,
            float(req.network_metrics.get("high_risk_counterparties", 0)) / 5.0,
            min(1.0, req.investigation_duration_sec / 3600.0),
            1.0 if len(req.missing_evidence_pillars) == 0 else 0.0
        ]

        return MemoryFeatureVector(
            risk_score=req.risk_score,
            rule_score=rule_s,
            ml_anomaly_score=ml_s,
            structuring_score=struct_s,
            velocity_score=vel_s,
            cash_ratio=cash_r,
            cross_border_ratio=cb_r,
            dense_vector=dense
        )

    def generate_semantic_embedding(self, text: str) -> List[float]:
        """Generates a 32-dimensional semantic dense embedding from investigation summary text."""
        if not text:
            return [0.0] * 32

        words = text.lower().split()
        vector = np.zeros(32)

        # Domain term hash projection algorithm
        for i, word in enumerate(words):
            h = abs(hash(word))
            idx = h % 32
            val = math.sin((i + 1) * 0.1) + math.cos(h % 17)
            vector[idx] += val

        # L2 Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()
