import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services';

export function useDashboardData() {
  return useQuery({
    queryKey: ['dashboardData'],
    queryFn: () => dashboardService.getDashboardData(),
    refetchInterval: 30_000, // Auto-refresh every 30 seconds
    staleTime: 25_000,
  });
}
