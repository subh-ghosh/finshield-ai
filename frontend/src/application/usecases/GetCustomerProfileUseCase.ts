import type { ICustomerRepository } from '../../domain/repositories/ICustomerRepository';
import type { CustomerProfile } from '../../domain/entities/CustomerProfile';

export class GetCustomerProfileUseCase {
  constructor(private customerRepository: ICustomerRepository) {}

  async execute(customerId: string): Promise<CustomerProfile> {
    return this.customerRepository.getCustomerProfile(customerId);
  }
}
