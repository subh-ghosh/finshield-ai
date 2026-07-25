import { useMutation } from '@tanstack/react-query';
import { plannerService } from '../services';
import type { PlannerResult } from '../types';

export function usePlannerInvestigation() {
  const {
    mutateAsync: investigate,
    data,
    isPending,
    error,
    reset,
  } = useMutation<PlannerResult, Error, string>({
    mutationFn: async (customerId: string) => {
      const result = await plannerService.runInvestigation(customerId);
      return result as PlannerResult;
    },
  });

  return {
    investigate,
    data,
    isPending,
    error,
    reset,
  };
}
