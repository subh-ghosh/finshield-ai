import { useQuery } from '@tanstack/react-query';
import { UseCases } from '../core/container';
import { queryKeys } from '../core/constants/queryKeys';
import type { QueueItem } from '../domain/entities/QueueItem';

export function useInvestigationQueue() {
  return useQuery<QueueItem[]>({
    queryKey: queryKeys.queue.all,
    queryFn: () => UseCases.getQueue.execute(),
    staleTime: 5 * 60 * 1000, // 5 minutes - queue doesn't change frequently
    refetchOnWindowFocus: true,
  });
}
