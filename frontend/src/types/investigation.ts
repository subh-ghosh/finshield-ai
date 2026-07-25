export interface Evidence {
  id: string | number;
  title: string;
  desc: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  confidence?: number;
  source?: string;
  timestamp?: string;
}

export interface RuleResult {
  rule_id: string;
  description: string;
  triggered: boolean;
  score_contribution: number;
}

export interface HybridRisk {
  composite_score: number;
  ml_anomaly_score: number;
  rule_base_score: number;
}

export interface Recommendation {
  action: 'SAR' | 'Close' | 'Escalate';
  reasoning: string;
}

export interface Investigation {
  id: string;
  customer_id: string;
  status: 'Open' | 'In Progress' | 'Pending Review' | 'Closed';
  assigned_analyst?: string;
  risk_profile: HybridRisk;
  evidences: Evidence[];
  rule_results: RuleResult[];
  recommendation?: Recommendation;
}
