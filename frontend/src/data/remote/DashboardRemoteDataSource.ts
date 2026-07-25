import { api } from '../../core/api';
import type { DashboardMetricsDTO } from '../dtos/DashboardMetricsDTO';

export class DashboardRemoteDataSource {
  async getMetrics(): Promise<DashboardMetricsDTO> {
    const response = await api.get<DashboardMetricsDTO>('/v1/metrics');
    return response.data;
  }
}
