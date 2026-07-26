import { useQuery } from '@tanstack/react-query';
import { SimilarCasesRepository } from '../data/repositories/SimilarCasesRepository';

const repo = new SimilarCasesRepository();

export const useSimilarCases = (investigationId: string, limit: number = 5) => {
  return useQuery({
    queryKey: ['similar_cases', investigationId, limit],
    queryFn: () => repo.getSimilarCases(investigationId, limit),
    enabled: Boolean(investigationId),
  });
};

export const useCaseComparison = (currentId: string, historicalCaseId: string | null) => {
  return useQuery({
    queryKey: ['case_comparison', currentId, historicalCaseId],
    queryFn: () => repo.getCaseComparison(currentId, historicalCaseId!),
    enabled: Boolean(currentId && historicalCaseId),
  });
};
