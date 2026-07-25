import { api } from '../../core/api';
import type { CustomerProfileDTO } from '../dtos/CustomerProfileDTO';

export class CustomerRemoteDataSource {
  async getCustomerProfile(customerId: string): Promise<CustomerProfileDTO> {
    const response = await api.get<CustomerProfileDTO>(`/v1/customer/${customerId}`);
    return response.data;
  }
}
