import type { CustomerProfile } from '../entities/CustomerProfile';

export interface ICustomerRepository {
  getCustomerProfile(customerId: string): Promise<CustomerProfile>;
}
