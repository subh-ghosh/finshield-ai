import { api } from '../../core/api';
import type { InvestigationResultDTO } from '../dtos/InvestigationResultDTO';

export class PlannerRemoteDataSource {
  async runInvestigation(customerId: string, request?: string): Promise<InvestigationResultDTO> {
    const response = await api.post<InvestigationResultDTO>('/v1/planner/investigate', {
      customer_id: customerId,
      ...(request ? { request } : {})
    });
    return response.data;
  }
}
