export interface CounterfactualSimulationResultDTO {
  customer_id: string;
  baseline_risk_score: number;
  baseline_recommendation: string;
  simulated_risk_score: number;
  simulated_recommendation: string;
  score_delta: number;
  recommendation_flipped: boolean;
  decision_boundary_thresholds: Record<string, number>;
  counterfactual_narrative: string;
  simulated_breakdown: {
    cash_deposit_impact: number;
    cross_border_impact: number;
    velocity_impact: number;
  };
}
