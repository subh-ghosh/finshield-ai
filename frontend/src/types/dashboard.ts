export interface DashboardMetrics {
  activeInvestigations: number;
  highRiskEntities: number;
  newAlerts: number;
  pendingReviews: number;
}

export interface RiskDistribution {
  name: string;
  value: number;
  color: string;
}

export interface AnomalyTrend {
  time: string;
  score: number;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  riskDistribution: RiskDistribution[];
  anomalyTrend: AnomalyTrend[];
}
