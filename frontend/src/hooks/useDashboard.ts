import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services';

export function useDashboardData() {
  return useQuery({
    queryKey: ['dashboardData'],
    queryFn: () => dashboardService.getDashboardData(),
  });
}
