import { useMutation } from '@tanstack/react-query';
import { api } from '../core/api';

export interface WhatIfRequest {
  customer_id: string;
  additional_cash_deposits_count: number;
  additional_cash_deposit_amount: number;
  cross_border_transfer_change_pct: number;
  velocity_multiplier: number;
}

export interface SimulationResult {
  customer_id: string;
  baseline_risk_score: number;
  baseline_recommendation: string;
  simulated_risk_score: number;
  simulated_recommendation: string;
  score_delta: number;
  recommendation_flipped: boolean;
  counterfactual_narrative: string;
  simulated_breakdown: Record<string, any>;
  risk_contributions: Record<string, any>;
  next_threshold_target: string;
  next_threshold_score: number;
  minimum_changes_required: string[];
}

export function useSimulation() {
  return useMutation({
    mutationFn: async (request: WhatIfRequest) => {
      const response = await api.post<{ data: SimulationResult }>('/v1/simulation/what-if', request);
      return response.data.data;
    },
  });
}
