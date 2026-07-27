import { PlannerRemoteDataSource } from '../remote/PlannerRemoteDataSource';
import { PlannerLocalDataSource } from '../local/PlannerLocalDataSource';
import { InvestigationMapper } from '../mappers/InvestigationMapper';
import type { InvestigationResult } from '../../domain/entities/InvestigationResult';
import type { IPlannerRepository } from '../../domain/repositories/IPlannerRepository';
import { Logger } from '../../core/observability/logger';

export class PlannerRepository implements IPlannerRepository {
  constructor(
    private remoteDataSource: PlannerRemoteDataSource,
    private localDataSource: PlannerLocalDataSource
  ) {}

  async runInvestigation(customerId: string, request?: string): Promise<InvestigationResult> {
    try {
      const dto = await this.remoteDataSource.runInvestigation(customerId, request);
      return InvestigationMapper.toDomain(dto);
    } catch (error) {
      Logger.warn(`Backend unavailable for Planner (Customer: ${customerId}). Falling back to local data source.`, { error });
      const fallbackDto = await this.localDataSource.runInvestigation(customerId, request);
      return InvestigationMapper.toDomain(fallbackDto);
    }
  }
}
