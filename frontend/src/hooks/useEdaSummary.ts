import { useQuery } from '@tanstack/react-query';
import { api } from '../core/api';

export interface EdaSummary {
  dataset_summary: {
    total_transactions: number;
    total_customers: number;
    fraud_transactions: number;
    fraud_rate_pct: number;
    source: string;
  };
  transaction_type_distribution: Record<string, number>;
  country_distribution: Record<string, number>;
  amount_statistics_usd: {
    mean: number;
    median: number;
    std: number;
    min: number;
    max: number;
    p95: number;
    p99: number;
  };
  customer_velocity_baseline: {
    mean_tx_count: number;
    max_tx_count: number;
    p95_tx_count: number;
  };
  risk_distribution: Record<string, number>;
  anomaly_detection: {
    isolation_forest_flagged: number;
    rule_engine_flagged: number;
  };
  top_10_risky_customers: Array<{
    customer_id: string;
    risk_score: number;
    recommendation: string;
    severity: string;
  }>;
}

export function useEdaSummary() {
  return useQuery<EdaSummary>({
    queryKey: ['eda-summary'],
    queryFn: async () => {
      const response = await api.get<EdaSummary>('/v1/eda/summary');
      return response.data;
    },
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}
