import { useQuery } from '@tanstack/react-query';
import { UseCases } from '../core/container';
import { queryKeys } from '../core/constants/queryKeys';
import type { CustomerProfile } from '../domain/entities/CustomerProfile';

export function useCustomerDetails(id: string) {
  return useQuery<CustomerProfile>({
    queryKey: queryKeys.customer.profile(id),
    queryFn: () => UseCases.getCustomerProfile.execute(id),
    staleTime: 300_000, // 5 minutes
    enabled: !!id,
  });
}
