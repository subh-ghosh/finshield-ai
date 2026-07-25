import type { DashboardMetricsDTO } from '../dtos/DashboardMetricsDTO';

export class DashboardLocalDataSource {
  async getMetrics(): Promise<DashboardMetricsDTO> {
    // Offline deterministic data matching the backend schema
    return {
      total_rows: 1323215,
      clean_rows: 1323215,
      engineered_customers: 9999,
      flagged_rules_count: 1999,
      flagged_anomalies_count: 0,
      execution_time_seconds: 0,
    };
  }
}
