export interface DashboardMetricsDTO {
  total_rows: number;
  clean_rows: number;
  engineered_customers: number;
  flagged_rules_count: number;
  flagged_anomalies_count: number;
  execution_time_seconds: number;
  timings?: Record<string, number>;
  // Optional real risk distribution from /api/v1/risk-classify/summary/distribution
  risk_distribution?: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}
