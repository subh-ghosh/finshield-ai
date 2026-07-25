import yaml
import os
from app.orchestrator.models.context import InvestigationContext

def load_thresholds(config_path: str = "app/orchestrator/config/thresholds.yaml"):
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("risk_thresholds", {})
    except Exception:
        # Fallback thresholds
        return {
            "FILE_SAR": 90,
            "ESCALATE": 70,
            "MANUAL_REVIEW": 50,
            "CLEAR": 0
        }

class DecisionEngine:
    def __init__(self, config_path: str = "app/orchestrator/config/thresholds.yaml"):
        self.thresholds = load_thresholds(config_path)

    def evaluate(self, context: InvestigationContext) -> dict:
        score = context.hybrid_risk_score
        
        recommendation = "CLEAR"
        risk_level = "LOW"
        confidence = 0.95
        reasons = []

        if score >= self.thresholds.get("FILE_SAR", 90):
            recommendation = "FILE_SAR"
            risk_level = "CRITICAL"
            reasons.append(f"Risk score ({score:.2f}) exceeds SAR threshold.")
        elif score >= self.thresholds.get("ESCALATE", 70):
            recommendation = "ESCALATE"
            risk_level = "HIGH"
            reasons.append(f"Risk score ({score:.2f}) indicates high risk requiring escalation.")
        elif score >= self.thresholds.get("MANUAL_REVIEW", 50):
            recommendation = "MANUAL_REVIEW"
            risk_level = "MEDIUM"
            reasons.append(f"Risk score ({score:.2f}) warrants manual review.")
        else:
            reasons.append(f"Risk score ({score:.2f}) is within acceptable limits.")

        if context.rule_hits:
            reasons.append(f"Triggered {len(context.rule_hits)} deterministic rules.")

        context.add_timeline_event("Decision Reached", f"Recommendation: {recommendation}")

        return {
            "recommendation": recommendation,
            "risk_level": risk_level,
            "confidence": confidence,
            "decision_reasons": reasons
        }
