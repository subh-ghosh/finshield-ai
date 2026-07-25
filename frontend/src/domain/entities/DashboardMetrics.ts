export interface DashboardMetrics {
  readonly activeInvestigations: number;
  readonly pendingReviews: number;
  readonly highRiskAlerts: number;
  readonly avgResolutionTime: string;
  readonly alerts: ReadonlyArray<{
    readonly id: string;
    readonly type: 'critical' | 'warning' | 'info';
    readonly message: string;
    readonly time: string;
  }>;
  readonly riskDistribution: ReadonlyArray<{
    readonly name: string;
    readonly value: number;
    readonly color: string;
  }>;
}
