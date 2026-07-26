import { api } from '../../core/api';
import type { DashboardMetricsDTO } from '../dtos/DashboardMetricsDTO';

export class DashboardRemoteDataSource {
  async getMetrics(): Promise<DashboardMetricsDTO> {
    // Fetch base pipeline metrics
    const metricsRes = await api.get<DashboardMetricsDTO>('/v1/metrics');
    const dto = metricsRes.data;

    // Also fetch real risk distribution from risk-classify summary endpoint
    try {
      const distRes = await api.get<any>('/v1/risk-classify/summary/distribution');
      const dist = distRes.data;
      if (dist?.distribution) {
        dto.risk_distribution = {
          low: dist.distribution.LOW || 0,
          medium: dist.distribution.MEDIUM || 0,
          high: dist.distribution.HIGH || 0,
          critical: dist.distribution.CRITICAL || 0,
        };
      }
    } catch {
      // Silently fall back - DashboardMapper will estimate from flagged counts
    }

    // Also fetch real anomaly count from the anomaly summary endpoint
    try {
      const anomalyRes = await api.get<any>('/v1/anomaly/summary/top?top_n=1');
      const anomalyData = anomalyRes.data;
      if (typeof anomalyData?.total_anomalies_detected === 'number') {
        dto.flagged_anomalies_count = anomalyData.total_anomalies_detected;
      }
    } catch {
      // Silently fall back
    }

    return dto;
  }
}
