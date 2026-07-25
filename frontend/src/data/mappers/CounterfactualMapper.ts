import type { CounterfactualSimulationResultDTO } from '../dtos/CounterfactualDTO';
import type { CounterfactualSimulationResult } from '../../domain/entities/Counterfactual';

export class CounterfactualMapper {
  static toDomain(dto: CounterfactualSimulationResultDTO): CounterfactualSimulationResult {
    return {
      customerId: dto.customer_id,
      baselineRiskScore: dto.baseline_risk_score,
      baselineRecommendation: dto.baseline_recommendation,
      simulatedRiskScore: dto.simulated_risk_score,
      simulatedRecommendation: dto.simulated_recommendation,
      scoreDelta: dto.score_delta,
      recommendationFlipped: dto.recommendation_flipped,
      decisionBoundaryThresholds: dto.decision_boundary_thresholds || {},
      counterfactualNarrative: dto.counterfactual_narrative,
      simulatedBreakdown: {
        cashDepositImpact: dto.simulated_breakdown?.cash_deposit_impact || 0,
        crossBorderImpact: dto.simulated_breakdown?.cross_border_impact || 0,
        velocityImpact: dto.simulated_breakdown?.velocity_impact || 0,
      },
    };
  }
}
