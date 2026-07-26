import type { InvestigationMemoryRecordDTO, MemorySearchResultDTO, MemoryStatisticsDTO } from '../dtos/InvestigationMemoryDTO';
import type { InvestigationMemoryRecord, MemorySearchResult, MemoryStatistics } from '../../domain/entities/InvestigationMemory';

export class InvestigationMemoryMapper {
  static toDomainRecord(dto: InvestigationMemoryRecordDTO): InvestigationMemoryRecord {
    return {
      memoryId: dto.memory_id,
      caseId: dto.case_id,
      customerId: dto.customer_id,
      customerName: dto.customer_name || 'Unknown',
      customerType: dto.customer_type || 'INDIVIDUAL',
      industry: dto.industry || 'General',
      jurisdiction: dto.jurisdiction || 'Domestic',
      investigationDate: dto.investigation_date,
      riskScore: dto.risk_score,
      finalDecision: dto.final_decision,
      disposition: dto.disposition,
      caseTypology: dto.case_typology || 'UNKNOWN_TYPOLOGY',
      triggeredRules: dto.triggered_rules || [],
      behavioralFeatures: dto.behavioral_features || {},
      isolationForestScore: dto.isolation_forest_score || 0,
      hybridRiskScore: dto.hybrid_risk_score || 0,
      networkMetrics: dto.network_metrics || {},
      evidenceSummary: dto.evidence_summary || [],
      complianceCompletenessScore: dto.compliance_completeness_score || 100,
      missingEvidencePillars: dto.missing_evidence_pillars || [],
      investigationSummary: dto.investigation_summary || '',
      sarNarrative: dto.sar_narrative,
      analystNotes: dto.analyst_notes,
      investigationDurationSec: dto.investigation_duration_sec || 0,
      featureVector: {
        riskScore: dto.feature_vector?.risk_score || 0,
        ruleScore: dto.feature_vector?.rule_score || 0,
        mlAnomalyScore: dto.feature_vector?.ml_anomaly_score || 0,
        structuringScore: dto.feature_vector?.structuring_score || 0,
        velocityScore: dto.feature_vector?.velocity_score || 0,
        cashRatio: dto.feature_vector?.cash_ratio || 0,
        crossBorderRatio: dto.feature_vector?.cross_border_ratio || 0,
        denseVector: dto.feature_vector?.dense_vector || [],
      },
      semanticEmbedding: dto.semantic_embedding || [],
      version: dto.version || 1,
      timestamp: dto.timestamp || Date.now(),
    };
  }

  static toDomainSearchResult(dto: MemorySearchResultDTO): MemorySearchResult {
    return {
      memoryRecord: this.toDomainRecord(dto.memory_record),
      similarityScore: dto.similarity_score,
      matchingFeatures: dto.matching_features || [],
    };
  }

  static toDomainStatistics(dto: MemoryStatisticsDTO): MemoryStatistics {
    return {
      totalStoredInvestigations: dto.total_stored_investigations || 0,
      decisions: dto.decisions || { FILE_SAR: 0, ESCALATE: 0, MANUAL_REVIEW: 0, CLEAR: 0 },
      averageRiskScore: dto.average_risk_score || 0,
      caseTypologies: dto.case_typologies || {},
      repositoryStatus: dto.repository_status || 'ACTIVE_ONLINE',
      lastUpdated: dto.last_updated || new Date().toISOString(),
    };
  }
}
