import { useMutation, useQueryClient } from '@tanstack/react-query';
import { UseCases } from '../core/container';
import type { InvestigationResult } from '../domain/entities/InvestigationResult';
import { queryKeys } from '../core/constants/queryKeys';

export function usePlannerInvestigation() {
  const queryClient = useQueryClient();

  const {
    mutateAsync: investigate,
    data,
    isPending,
    error,
    reset,
  } = useMutation<InvestigationResult, Error, string>({
    mutationFn: async (customerId: string) => {
      return await UseCases.runInvestigation.execute(customerId);
    },
    onSuccess: (result, customerId) => {
      // Phase 10: Cache Strategy - invalidate queries
      queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.investigation.detail(customerId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.metrics });
    }
  });

  return {
    investigate,
    data,
    isPending,
    error,
    reset,
  };
}
