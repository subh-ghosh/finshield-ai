import { DashboardRemoteDataSource } from '../remote/DashboardRemoteDataSource';
import { DashboardMapper } from '../mappers/DashboardMapper';
import type { DashboardMetrics } from '../../domain/entities/DashboardMetrics';
import type { IDashboardRepository } from '../../domain/repositories/IDashboardRepository';

export class DashboardRepository implements IDashboardRepository {
  constructor(
    private remoteDataSource: DashboardRemoteDataSource
  ) {}

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const dto = await this.remoteDataSource.getMetrics();
    return DashboardMapper.toDomain(dto);
  }
}
