import type { IDashboardRepository } from '../../domain/repositories/IDashboardRepository';
import type { DashboardMetrics } from '../../domain/entities/DashboardMetrics';

export class GetDashboardMetricsUseCase {
  constructor(private dashboardRepository: IDashboardRepository) {}

  async execute(): Promise<DashboardMetrics> {
    return this.dashboardRepository.getDashboardMetrics();
  }
}
