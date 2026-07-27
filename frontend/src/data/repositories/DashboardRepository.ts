import { DashboardRemoteDataSource } from '../remote/DashboardRemoteDataSource';
import { DashboardLocalDataSource } from '../local/DashboardLocalDataSource';
import { DashboardMapper } from '../mappers/DashboardMapper';
import type { DashboardMetrics } from '../../domain/entities/DashboardMetrics';
import { Logger } from '../../core/observability/logger';
import type { IDashboardRepository } from '../../domain/repositories/IDashboardRepository';

export class DashboardRepository implements IDashboardRepository {
  constructor(
    private remoteDataSource: DashboardRemoteDataSource,
    private localDataSource: DashboardLocalDataSource
  ) {}

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const dto = await this.remoteDataSource.getMetrics();
    return DashboardMapper.toDomain(dto);
  }
}
