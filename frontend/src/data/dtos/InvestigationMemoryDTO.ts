export interface InvestigationMemoryRecordDTO {
  memory_id: string;
  case_id: string;
  customer_id: string;
  customer_name: string;
  customer_type: string;
  industry: string;
  jurisdiction: string;
  investigation_date: string;
  risk_score: number;
  final_decision: string;
  disposition: string;
  case_typology: string;
  triggered_rules: string[];
  behavioral_features: Record<string, number>;
  isolation_forest_score: number;
  hybrid_risk_score: number;
  network_metrics: Record<string, any>;
  evidence_summary: string[];
  compliance_completeness_score: number;
  missing_evidence_pillars: string[];
  investigation_summary: string;
  sar_narrative?: string;
  analyst_notes?: string;
  investigation_duration_sec: number;
  feature_vector: {
    risk_score: number;
    rule_score: number;
    ml_anomaly_score: number;
    structuring_score: number;
    velocity_score: number;
    cash_ratio: number;
    cross_border_ratio: number;
    dense_vector: number[];
  };
  semantic_embedding: number[];
  version: number;
  timestamp: number;
}

export interface MemorySearchResultDTO {
  memory_record: InvestigationMemoryRecordDTO;
  similarity_score: number;
  matching_features: string[];
}

export interface MemoryStatisticsDTO {
  total_stored_investigations: number;
  decisions: {
    FILE_SAR: number;
    ESCALATE: number;
    MANUAL_REVIEW: number;
    CLEAR: number;
  };
  average_risk_score: number;
  case_typologies: Record<string, number>;
  repository_status: string;
  last_updated: string;
}
