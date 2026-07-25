import { useQuery } from '@tanstack/react-query';
import { customerService } from '../services';

export function useCustomerDetails(id: string) {
  return useQuery({
    queryKey: ['customer', id],
    queryFn: () => customerService.getCustomerById(id),
    enabled: !!id,
  });
}
