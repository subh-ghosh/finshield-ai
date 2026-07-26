"""REST API Router for Counterfactual What-If Simulation."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.api.v1.schemas.responses import ApiResponse
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
from app.services.counterfactual_simulator import CounterfactualRiskSimulator
from app.models.counterfactual import CounterfactualSimulationRequest
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Simulation"])

_simulator = CounterfactualRiskSimulator()


class WhatIfRequest(BaseModel):
    """Request body for what-if simulation."""
    customer_id: str = Field(..., description="Target customer ID")
    additional_cash_deposits_count: int = Field(default=0, ge=0, description="Number of additional cash deposits")
    additional_cash_deposit_amount: float = Field(default=0.0, ge=0, description="Amount per cash deposit")
    cross_border_transfer_change_pct: float = Field(default=0.0, description="Cross-border transfer % change")
    velocity_multiplier: float = Field(default=1.0, ge=0.1, description="Transaction velocity multiplier")


@router.post(
    "/simulation/what-if",
    response_model=ApiResponse[dict],
    summary="Run What-If Simulation",
    description="Simulates the impact of hypothetical transactions on a customer's risk score."
)
def run_what_if_simulation(
    request: WhatIfRequest,
    pipeline_result: PipelineResult = Depends(get_pipeline_result)
) -> ApiResponse[dict]:
    """Runs a counterfactual simulation for a customer.
    
    Accepts hypothetical transaction parameters and returns predicted 
    risk score changes, triggered rules, and ML anomaly deltas without 
    modifying actual data.
    """
    try:
        # Find baseline risk score for this customer
        baseline_score = 41.0  # Default fallback
        baseline_recommendation = "MANUAL_REVIEW"
        
        if hasattr(pipeline_result, "hybrid_risk_analysis") and pipeline_result.hybrid_risk_analysis:
            for r in pipeline_result.hybrid_risk_analysis:
                if str(r.customer_id) == request.customer_id:
                    baseline_score = float(r.overall_risk_score * 100)
                    baseline_recommendation = str(r.recommendation)
                    break

        # Build simulation request
        sim_request = CounterfactualSimulationRequest(
            customer_id=request.customer_id,
            additional_cash_deposits_count=request.additional_cash_deposits_count,
            additional_cash_deposit_amount=request.additional_cash_deposit_amount,
            cross_border_transfer_change_pct=request.cross_border_transfer_change_pct,
            velocity_multiplier=request.velocity_multiplier
        )

        # Run simulation
        result = _simulator.simulate(
            request=sim_request,
            baseline_score_0_100=baseline_score,
            baseline_recommendation=baseline_recommendation
        )

        # Serialize result
        result_dict = {
            "customer_id": result.customer_id,
            "baseline_risk_score": result.baseline_risk_score,
            "baseline_recommendation": result.baseline_recommendation,
            "simulated_risk_score": result.simulated_risk_score,
            "simulated_recommendation": result.simulated_recommendation,
            "score_delta": result.score_delta,
            "recommendation_flipped": result.recommendation_flipped,
            "counterfactual_narrative": result.counterfactual_narrative,
            "simulated_breakdown": result.simulated_breakdown,
            "risk_contributions": result.risk_contributions,
            "next_threshold_target": result.next_threshold_target,
            "next_threshold_score": result.next_threshold_score,
            "minimum_changes_required": result.minimum_changes_required,
        }

        return ApiResponse(data=result_dict)

    except Exception as e:
        logger.error(f"Simulation failed for {request.customer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Simulation engine error.")
