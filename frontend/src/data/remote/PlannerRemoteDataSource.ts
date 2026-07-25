import { api } from '../../core/api';
import type { InvestigationResultDTO } from '../dtos/InvestigationResultDTO';

export class PlannerRemoteDataSource {
  async runInvestigation(customerId: string): Promise<InvestigationResultDTO> {
    const response = await api.post<InvestigationResultDTO>('/v1/planner/investigate', {
      customer_id: customerId,
    });
    return response.data;
  }
}
