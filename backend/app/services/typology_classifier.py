"""Deterministic AML Typology Classifier Engine."""

from typing import List, Dict, Any
from app.models.investigation_memory import CaseTypology, StoreMemoryRequest


class TypologyClassifier:
    """Classifies investigation patterns into AML typologies deterministically."""

    def classify(self, req: StoreMemoryRequest) -> CaseTypology:
        rules_lower = [r.lower() for r in req.triggered_rules]
        beh = req.behavioral_features or {}
        jurisdiction = (req.jurisdiction or "").upper()
        summary_lower = (req.investigation_summary or "").lower()

        # 1. Sanctions Screening
        if any("sanction" in r for r in rules_lower) or "sanction" in summary_lower:
            return CaseTypology.SANCTIONS

        # 2. Terrorism Financing
        if "terrorism" in summary_lower or "pep_high_risk" in rules_lower:
            return CaseTypology.TERRORISM_FINANCING

        # 3. High Risk Jurisdiction
        high_risk_countries = ["IRAN", "NORTH KOREA", "SYRIA", "RUSSIA", "MYANMAR", "CAYMAN ISLANDS"]
        if any(c in jurisdiction for c in high_risk_countries) or any("high_risk" in r for r in rules_lower):
            return CaseTypology.HIGH_RISK_JURISDICTION

        # 4. Cash Structuring & Smurfing
        structuring_score = beh.get("structuring_indicator", 0.0)
        cash_ratio = beh.get("cash_ratio", 0.0)
        if structuring_score > 0.4 or any("structuring" in r for r in rules_lower) or cash_ratio > 0.6:
            if beh.get("recipient_diversity", 0.0) > 0.7:
                return CaseTypology.SMURFING
            return CaseTypology.STRUCTURING

        # 5. Money Mule / Funnel Account
        velocity = beh.get("velocity_multiplier", 1.0)
        if velocity > 3.0 and beh.get("rapid_pass_through", 0.0) > 0.7:
            if beh.get("multi_state_deposits", 0.0) > 0.5:
                return CaseTypology.FUNNEL_ACCOUNT
            return CaseTypology.MONEY_MULE

        # 6. Layering
        if velocity > 2.0 or any("layering" in r for r in rules_lower):
            return CaseTypology.LAYERING

        # 7. Crypto
        if "crypto" in summary_lower or any("crypto" in r for r in rules_lower):
            return CaseTypology.CRYPTO

        # 8. Shell Company
        if req.risk_score >= 65.0 and req.industry.lower() in ["general", "consulting", "holding"] and req.missing_evidence_pillars:
            return CaseTypology.SHELL_COMPANY

        # Default Fallback
        if req.risk_score >= 65.0:
            return CaseTypology.LAYERING

        return CaseTypology.UNKNOWN
