import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { MemoryRepository } from '../data/repositories/MemoryRepository';
import type { StoreMemoryRequest } from '../domain/entities/InvestigationMemory';

const memoryRepo = new MemoryRepository();

export const useMemoryStatistics = () => {
  return useQuery({
    queryKey: ['memory_statistics'],
    queryFn: () => memoryRepo.getStatistics(),
    refetchInterval: 30000,
  });
};

export const useCustomerMemoryRecords = (customerId: string) => {
  return useQuery({
    queryKey: ['memory_customer', customerId],
    queryFn: () => memoryRepo.getMemoryByCustomer(customerId),
    enabled: Boolean(customerId),
  });
};

export const useMemorySearch = (params: {
  queryText?: string;
  customerId?: string;
  jurisdiction?: string;
  industry?: string;
  finalDecision?: string;
  minRiskScore?: number;
  maxRiskScore?: number;
  limit?: number;
}) => {
  return useQuery({
    queryKey: ['memory_search', params],
    queryFn: () => memoryRepo.searchMemory(params),
  });
};

export const useStoreMemory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: StoreMemoryRequest) => memoryRepo.storeMemory(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['memory_statistics'] });
      queryClient.invalidateQueries({ queryKey: ['memory_customer', data.customerId] });
    },
  });
};
