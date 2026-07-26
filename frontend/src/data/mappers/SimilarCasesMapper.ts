import type { SimilarCasesResponseDTO, SimilarCaseResultDTO, CaseComparisonResultDTO } from '../dtos/SimilarCasesDTO';
import type { SimilarCasesResponse, SimilarCaseResult, CaseComparisonResult } from '../../domain/entities/SimilarCases';
import { InvestigationMemoryMapper } from './InvestigationMemoryMapper';

export class SimilarCasesMapper {
  static toDomainResponse(dto: SimilarCasesResponseDTO): SimilarCasesResponse {
    return {
      currentInvestigationId: dto.current_investigation_id,
      totalMatchesFound: dto.total_matches_found,
      executiveSimilaritySummary: dto.executive_similarity_summary,
      averageSimilarityPct: dto.average_similarity_pct,
      similarCases: (dto.similar_cases || []).map(item => this.toDomainResult(item)),
    };
  }

  static toDomainResult(dto: SimilarCaseResultDTO): SimilarCaseResult {
    return {
      caseId: dto.case_id,
      customerId: dto.customer_id,
      customerName: dto.customer_name || 'Unknown',
      riskScore: dto.risk_score,
      finalDecision: dto.final_decision,
      caseOutcome: dto.case_outcome || 'CLOSED',
      caseTypology: dto.case_typology || 'UNKNOWN_TYPOLOGY',
      investigationDate: dto.investigation_date,
      investigationDurationSec: dto.investigation_duration_sec || 0,
      estimatedAnalystTimeSavedMin: dto.estimated_analyst_time_saved_min || 35,
      primaryRules: dto.primary_rules || [],
      similarityBreakdown: {
        featureVectorSimilarity: dto.similarity_breakdown?.feature_vector_similarity || 0,
        narrativeSimilarity: dto.similarity_breakdown?.narrative_similarity || 0,
        ruleOverlapScore: dto.similarity_breakdown?.rule_overlap_score || 0,
        typologyMatchScore: dto.similarity_breakdown?.typology_match_score || 0,
        customerProfileSimilarity: dto.similarity_breakdown?.customer_profile_similarity || 0,
        jurisdictionSimilarity: dto.similarity_breakdown?.jurisdiction_similarity || 0,
        timelineSimilarity: dto.similarity_breakdown?.timeline_similarity || 0,
        overallSimilarityScore: dto.similarity_breakdown?.overall_similarity_score || 0,
      },
      deterministicReasons: dto.deterministic_reasons || [],
      memoryRecord: InvestigationMemoryMapper.toDomainRecord(dto.memory_record),
    };
  }

  static toDomainComparison(dto: CaseComparisonResultDTO): CaseComparisonResult {
    return {
      currentInvestigationId: dto.current_investigation_id,
      historicalCaseId: dto.historical_case_id,
      overallSimilarityPct: dto.overall_similarity_pct,
      executiveComparisonSummary: dto.executive_comparison_summary,
      riskScoreComparison: dto.risk_score_comparison || { current: 0, historical: 0 },
      decisionComparison: dto.decision_comparison || { current: 'UNKNOWN', historical: 'UNKNOWN' },
      typologyComparison: dto.typology_comparison || { current: 'UNKNOWN', historical: 'UNKNOWN' },
      rulesComparison: dto.rules_comparison || { current: [], historical: [] },
      matchingIndicators: dto.matching_indicators || [],
      differenceHighlights: dto.difference_highlights || [],
    };
  }
}
