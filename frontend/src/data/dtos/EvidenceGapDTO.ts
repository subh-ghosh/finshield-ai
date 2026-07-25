export interface ComplianceItemEvaluationDTO {
  pillar: string;
  name: string;
  status: string;
  weight: number;
  is_required_for_sar: boolean;
  description: string;
  remediation_action: string;
}

export interface EvidenceGapAssessmentDTO {
  customer_id: string;
  completeness_score: number;
  sar_filing_ready: boolean;
  blocking_critical_gaps_count: number;
  total_items_evaluated: number;
  passed_items_count: number;
  evaluations: ComplianceItemEvaluationDTO[];
  warnings: string[];
  missing_critical_items: string[];
  missing_optional_items: string[];
  remediation_roadmap: string[];
}
