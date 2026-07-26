import { api } from '../../core/api';
import type { SimilarCasesResponse, CaseComparisonResult } from '../../domain/entities/SimilarCases';
import type { SimilarCasesResponseDTO, CaseComparisonResultDTO } from '../dtos/SimilarCasesDTO';
import { SimilarCasesMapper } from '../mappers/SimilarCasesMapper';

export class SimilarCasesRepository {
  async getSimilarCases(investigationId: string, limit: number = 5): Promise<SimilarCasesResponse> {
    const cleanId = investigationId.replace('CUST-', 'C_');
    const res = await api.get<SimilarCasesResponseDTO>(`/v1/similar-cases/${cleanId}`, {
      params: { limit },
    });
    return SimilarCasesMapper.toDomainResponse(res.data);
  }

  async getCaseComparison(currentId: string, historicalCaseId: string): Promise<CaseComparisonResult> {
    const cleanId = currentId.replace('CUST-', 'C_');
    const res = await api.get<CaseComparisonResultDTO>(`/v1/similar-cases/${cleanId}/comparison`, {
      params: { historical_case_id: historicalCaseId },
    });
    return SimilarCasesMapper.toDomainComparison(res.data);
  }
}
