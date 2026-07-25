import { useQuery } from '@tanstack/react-query';
import { UseCases } from '../core/container';
import { queryKeys } from '../core/constants/queryKeys';
import type { InvestigationResult } from '../domain/entities/InvestigationResult';

export function useInvestigationData(id: string) {
  return useQuery<InvestigationResult>({
    queryKey: queryKeys.investigation.detail(id),
    queryFn: () => UseCases.runInvestigation.execute(id),
    enabled: !!id,
    refetchOnWindowFocus: false, // Do not rerun investigation on window focus
    staleTime: Infinity, // Investigation reports are immutable
  });
}
