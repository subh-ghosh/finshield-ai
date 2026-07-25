import { useQuery } from '@tanstack/react-query';
import { queueService } from '../services';

export function useInvestigationQueue() {
  return useQuery({
    queryKey: ['investigationQueue'],
    queryFn: () => queueService.getInvestigationQueue(),
  });
}
