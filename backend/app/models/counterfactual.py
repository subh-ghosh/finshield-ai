"""Pydantic data models for the Counterfactual Risk Simulator."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class CounterfactualSimulationRequest(BaseModel):
    customer_id: str = Field(..., description="Target customer identifier.")
    additional_cash_deposits_count: int = Field(default=0, ge=0, le=20, description="Number of additional cash deposits.")
    additional_cash_deposit_amount: float = Field(default=0.0, ge=0.0, description="Individual cash deposit amount in INR/USD.")
    cross_border_transfer_change_pct: float = Field(default=0.0, ge=-100.0, le=500.0, description="Percentage change in cross-border transfers.")
    velocity_multiplier: float = Field(default=1.0, ge=0.1, le=10.0, description="Velocity multiplier.")


class ContributionItem(BaseModel):
    category: str
    points: float
    percentage: float
    reason: str
    confidence: float = 0.95
    subsystem: str


class CounterfactualSimulationResult(BaseModel):
    customer_id: str
    baseline_risk_score: float = Field(..., ge=0.0, le=100.0)
    baseline_recommendation: str
    simulated_risk_score: float = Field(..., ge=0.0, le=100.0)
    simulated_recommendation: str
    score_delta: float
    recommendation_flipped: bool
    decision_boundary_thresholds: Dict[str, float]
    counterfactual_narrative: str
    simulated_breakdown: Dict[str, float]
    risk_contributions: Dict[str, float] = Field(default_factory=dict)
    detailed_contributions: List[ContributionItem] = Field(default_factory=list)
    next_threshold_target: Optional[str] = None
    next_threshold_score: Optional[float] = None
    minimum_changes_required: List[str] = Field(default_factory=list)


