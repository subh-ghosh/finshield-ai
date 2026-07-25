import { useQuery } from '@tanstack/react-query';
import { UseCases } from '../core/container';
import { queryKeys } from '../core/constants/queryKeys';
import type { DashboardMetrics } from '../domain/entities/DashboardMetrics';

export function useDashboardData() {
  return useQuery<DashboardMetrics>({
    queryKey: queryKeys.dashboard.metrics,
    queryFn: () => UseCases.getDashboardMetrics.execute(),
    refetchInterval: 30_000, // Auto-refresh every 30 seconds
    staleTime: 30_000,
  });
}
