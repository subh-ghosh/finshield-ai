import { api } from '../../core/api';

import type { StoreMemoryRequest, InvestigationMemoryRecord, MemorySearchResult, MemoryStatistics } from '../../domain/entities/InvestigationMemory';
import type { InvestigationMemoryRecordDTO, MemorySearchResultDTO, MemoryStatisticsDTO } from '../dtos/InvestigationMemoryDTO';
import { InvestigationMemoryMapper } from '../mappers/InvestigationMemoryMapper';

export class MemoryRepository {
  async storeMemory(request: StoreMemoryRequest): Promise<InvestigationMemoryRecord> {
    const payload = {
      case_id: request.caseId,
      customer_id: request.customerId,
      customer_name: request.customerName || 'Unknown',
      customer_type: request.customerType || 'INDIVIDUAL',
      industry: request.industry || 'General',
      jurisdiction: request.jurisdiction || 'Domestic',
      risk_score: request.riskScore,
      final_decision: request.finalDecision,
      disposition: request.disposition || 'CASE_CLOSED',
      triggered_rules: request.triggeredRules || [],
      behavioral_features: request.behavioralFeatures || {},
      isolation_forest_score: request.isolationForestScore || 0,
      hybrid_risk_score: request.hybridRiskScore || 0,
      network_metrics: request.networkMetrics || {},
      evidence_summary: request.evidenceSummary || [],
      compliance_completeness_score: request.complianceCompletenessScore || 100,
      missing_evidence_pillars: request.missingEvidencePillars || [],
      investigation_summary: request.investigationSummary || '',
      sar_narrative: request.sarNarrative,
      analyst_notes: request.analystNotes,
      investigation_duration_sec: request.investigationDurationSec || 0,
      case_typology: request.caseTypology || 'UNKNOWN_TYPOLOGY',
    };

    const res = await api.post<InvestigationMemoryRecordDTO>('/v1/memory/store', payload);

    return InvestigationMemoryMapper.toDomainRecord(res.data);
  }

  async searchMemory(params: {
    queryText?: string;
    customerId?: string;
    jurisdiction?: string;
    industry?: string;
    finalDecision?: string;
    minRiskScore?: number;
    maxRiskScore?: number;
    limit?: number;
  }): Promise<MemorySearchResult[]> {
    const res = await api.get<MemorySearchResultDTO[]>('/v1/memory/search', {
      params: {
        query_text: params.queryText,
        customer_id: params.customerId,
        jurisdiction: params.jurisdiction,
        industry: params.industry,
        final_decision: params.finalDecision,
        min_risk_score: params.minRiskScore,
        max_risk_score: params.maxRiskScore,
        limit: params.limit || 10,
      },
    });

    return res.data.map(dto => InvestigationMemoryMapper.toDomainSearchResult(dto));
  }

  async getStatistics(): Promise<MemoryStatistics> {
    const res = await api.get<MemoryStatisticsDTO>('/v1/memory/statistics');
    return InvestigationMemoryMapper.toDomainStatistics(res.data);
  }

  async getMemoryByCustomer(customerId: string): Promise<InvestigationMemoryRecord[]> {
    const cleanId = customerId.replace('CUST-', 'C_');
    const res = await api.get<InvestigationMemoryRecordDTO[]>(`/v1/memory/customer/${cleanId}`);

    return res.data.map(dto => InvestigationMemoryMapper.toDomainRecord(dto));
  }
}
