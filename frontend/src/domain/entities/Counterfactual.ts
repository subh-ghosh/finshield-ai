export interface CounterfactualSimulationRequest {
  customerId: string;
  additionalCashDepositsCount: number;
  additionalCashDepositAmount: number;
  crossBorderTransferChangePct: number;
  velocityMultiplier: number;
}

export interface CounterfactualSimulationResult {
  customerId: string;
  baselineRiskScore: number;
  baselineRecommendation: string;
  simulatedRiskScore: number;
  simulatedRecommendation: string;
  scoreDelta: number;
  recommendationFlipped: boolean;
  decisionBoundaryThresholds: Record<string, number>;
  counterfactualNarrative: string;
  simulatedBreakdown: {
    cashDepositImpact: number;
    crossBorderImpact: number;
    velocityImpact: number;
  };
}
