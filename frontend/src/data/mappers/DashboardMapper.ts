import type { DashboardMetricsDTO } from '../dtos/DashboardMetricsDTO';
import type { DashboardMetrics } from '../../domain/entities/DashboardMetrics';

export class DashboardMapper {
  static toDomain(dto: DashboardMetricsDTO): DashboardMetrics {
    // Use real risk distribution if available from /api/v1/risk-classify/summary/distribution
    // otherwise estimate from flagged counts
    const realDist = dto.risk_distribution;
    const riskDistribution = realDist
      ? [
          { name: 'Low',      value: realDist.low,      color: '#10B981' },
          { name: 'Medium',   value: realDist.medium,   color: '#F59E0B' },
          { name: 'High',     value: realDist.high,     color: '#F97316' },
          { name: 'Critical', value: realDist.critical, color: '#EF4444' },
        ]
      : [
          { name: 'Low',      value: dto.engineered_customers - (dto.flagged_rules_count + dto.flagged_anomalies_count), color: '#10B981' },
          { name: 'Medium',   value: Math.floor(dto.flagged_rules_count * 0.6),  color: '#F59E0B' },
          { name: 'High',     value: Math.floor(dto.flagged_rules_count * 0.25), color: '#F97316' },
          { name: 'Critical', value: Math.floor(dto.flagged_rules_count * 0.15), color: '#EF4444' },
        ];

    const highRiskAlerts = realDist
      ? realDist.high + realDist.critical
      : Math.floor(dto.flagged_rules_count * 0.15);

    return {
      activeInvestigations: dto.flagged_rules_count + dto.flagged_anomalies_count,
      pendingReviews: Math.floor((dto.flagged_rules_count + dto.flagged_anomalies_count) * 0.3),
      highRiskAlerts,
      avgResolutionTime: '2.4h',
      alerts: [
        {
          id: '1',
          type: 'critical',
          message: `${dto.flagged_rules_count} AML Rules Triggered in batch execution`,
          time: new Date().toISOString(),
        },
        {
          id: '2',
          type: 'warning',
          message: `${dto.flagged_anomalies_count} Isolation Forest Anomalies Detected`,
          time: new Date(Date.now() - 3600000).toISOString(),
        },
      ],
      riskDistribution,
    };
  }
}
