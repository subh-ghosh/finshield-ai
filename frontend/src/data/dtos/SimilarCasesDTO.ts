import type { InvestigationMemoryRecordDTO } from './InvestigationMemoryDTO';

export interface SimilarityBreakdownDTO {
  feature_vector_similarity: number;
  narrative_similarity: number;
  rule_overlap_score: number;
  typology_match_score: number;
  customer_profile_similarity: number;
  jurisdiction_similarity: number;
  timeline_similarity: number;
  overall_similarity_score: number;
}

export interface SimilarCaseResultDTO {
  case_id: string;
  customer_id: string;
  customer_name: string;
  risk_score: number;
  final_decision: string;
  case_outcome: string;
  case_typology: string;
  investigation_date: string;
  investigation_duration_sec: number;
  estimated_analyst_time_saved_min: number;
  primary_rules: string[];
  similarity_breakdown: SimilarityBreakdownDTO;
  deterministic_reasons: string[];
  memory_record: InvestigationMemoryRecordDTO;
}

export interface SimilarCasesResponseDTO {
  current_investigation_id: string;
  total_matches_found: number;
  executive_similarity_summary: string;
  average_similarity_pct: number;
  similar_cases: SimilarCaseResultDTO[];
}

export interface CaseComparisonResultDTO {
  current_investigation_id: string;
  historical_case_id: string;
  overall_similarity_pct: number;
  executive_comparison_summary: string;
  risk_score_comparison: { current: number; historical: number };
  decision_comparison: { current: string; historical: string };
  typology_comparison: { current: string; historical: string };
  rules_comparison: { current: string[]; historical: string[] };
  matching_indicators: string[];
  difference_highlights: string[];
}
