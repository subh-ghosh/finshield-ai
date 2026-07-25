"""Deterministic Counterfactual Risk Simulation Engine."""

import math
from typing import Dict, Any
from app.models.counterfactual import (
    CounterfactualSimulationRequest,
    CounterfactualSimulationResult
)


class CounterfactualRiskSimulator:
    """Simulates decision sensitivity and risk score shifts mathematically."""

    DECISION_THRESHOLDS = {
        "CLEAR_MAX": 34.9,
        "MANUAL_REVIEW_MIN": 35.0,
        "MANUAL_REVIEW_MAX": 64.9,
        "ESCALATE_MIN": 65.0,
        "ESCALATE_MAX": 84.9,
        "FILE_SAR_MIN": 85.0
    }

    def simulate(
        self,
        request: CounterfactualSimulationRequest,
        baseline_score_0_100: float,
        baseline_recommendation: str
    ) -> CounterfactualSimulationResult:
        customer_id = request.customer_id
        b_score = float(baseline_score_0_100)

        # 1. Calculate Cash Structuring Impact
        n_deposits = request.additional_cash_deposits_count
        amt_deposit = request.additional_cash_deposit_amount
        total_additional_cash = n_deposits * amt_deposit

        cash_delta = 0.0
        if total_additional_cash > 0:
            # Sub-threshold structuring deposits (< 10,000) carry higher risk penalty
            structuring_penalty = 1.35 if (8000 <= amt_deposit <= 9999) else 1.0
            cash_delta = min(38.0, (total_additional_cash / 4500.0) * 7.5 * structuring_penalty)

        # 2. Calculate Cross-Border Shift Impact
        cb_pct = request.cross_border_transfer_change_pct
        cb_delta = (cb_pct / 100.0) * 18.0

        # 3. Calculate Velocity Impact
        vel_mult = request.velocity_multiplier
        vel_delta = (vel_mult - 1.0) * 12.0

        # 4. Compute Simulated Risk Score
        total_delta = cash_delta + cb_delta + vel_delta
        simulated_score = round(max(5.0, min(98.0, b_score + total_delta)), 1)
        score_delta = round(simulated_score - b_score, 1)

        # 5. Classify Simulated Recommendation
        simulated_recommendation = self._classify_recommendation(simulated_score)
        recommendation_flipped = (simulated_recommendation != baseline_recommendation)

        # 6. Generate Deterministic Counterfactual Narrative
        narrative = self._generate_narrative(
            customer_id=customer_id,
            baseline_score=b_score,
            baseline_rec=baseline_recommendation,
            simulated_score=simulated_score,
            simulated_rec=simulated_recommendation,
            n_deposits=n_deposits,
            amt_deposit=amt_deposit,
            cb_pct=cb_pct,
            score_delta=score_delta
        )

        return CounterfactualSimulationResult(
            customer_id=customer_id,
            baseline_risk_score=b_score,
            baseline_recommendation=baseline_recommendation,
            simulated_risk_score=simulated_score,
            simulated_recommendation=simulated_recommendation,
            score_delta=score_delta,
            recommendation_flipped=recommendation_flipped,
            decision_boundary_thresholds=self.DECISION_THRESHOLDS,
            counterfactual_narrative=narrative,
            simulated_breakdown={
                "cash_deposit_impact": round(cash_delta, 1),
                "cross_border_impact": round(cb_delta, 1),
                "velocity_impact": round(vel_delta, 1)
            }
        )

    def _classify_recommendation(self, score: float) -> str:
        if score >= self.DECISION_THRESHOLDS["FILE_SAR_MIN"]:
            return "FILE_SAR"
        if score >= self.DECISION_THRESHOLDS["ESCALATE_MIN"]:
            return "ESCALATE"
        if score >= self.DECISION_THRESHOLDS["MANUAL_REVIEW_MIN"]:
            return "MANUAL_REVIEW"
        return "CLEAR"

    def _generate_narrative(
        self,
        customer_id: str,
        baseline_score: float,
        baseline_rec: str,
        simulated_score: float,
        simulated_rec: str,
        n_deposits: int,
        amt_deposit: float,
        cb_pct: float,
        score_delta: float
    ) -> str:
        parts = []

        if n_deposits > 0:
            parts.append(f"adding {n_deposits} cash deposit(s) of ₹{amt_deposit:,.2f} each")
        if cb_pct != 0.0:
            direction = "increasing" if cb_pct > 0 else "decreasing"
            parts.append(f"{direction} cross-border transfers by {abs(cb_pct):.0f}%")

        action_desc = " and ".join(parts) if parts else "no baseline shifts"
        direction_str = "increases" if score_delta >= 0 else "decreases"

        if simulated_rec != baseline_rec:
            return (
                f"If {action_desc}, composite risk score {direction_str} from {baseline_score:.0f} to {simulated_score:.0f} "
                f"(+{score_delta:+.1f} pts), flipping compliance recommendation from `{baseline_rec}` to `{simulated_rec}`."
            )
        else:
            return (
                f"If {action_desc}, composite risk score {direction_str} from {baseline_score:.0f} to {simulated_score:.0f} "
                f"({score_delta:+.1f} pts). Recommendation remains `{baseline_rec}`."
            )
