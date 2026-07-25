import { useQuery } from '@tanstack/react-query';
import { investigationService } from '../services';

export function useInvestigationData(id: string) {
  return useQuery({
    queryKey: ['investigation', id],
    queryFn: () => investigationService.getInvestigationById(id),
    enabled: !!id,
  });
}
