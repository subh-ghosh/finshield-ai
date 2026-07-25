import type { DashboardMetrics } from '../entities/DashboardMetrics';

export interface IDashboardRepository {
  getDashboardMetrics(): Promise<DashboardMetrics>;
}
