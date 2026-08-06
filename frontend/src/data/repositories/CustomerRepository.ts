import { CustomerRemoteDataSource } from '../remote/CustomerRemoteDataSource';
import { CustomerMapper } from '../mappers/CustomerMapper';
import type { CustomerProfile } from '../../domain/entities/CustomerProfile';
import type { ICustomerRepository } from '../../domain/repositories/ICustomerRepository';

export class CustomerRepository implements ICustomerRepository {
  constructor(
    private remoteDataSource: CustomerRemoteDataSource
  ) {}

  async getCustomerProfile(customerId: string): Promise<CustomerProfile> {
    const dto = await this.remoteDataSource.getCustomerProfile(customerId);
    return CustomerMapper.toDomain(dto);
  }
}
