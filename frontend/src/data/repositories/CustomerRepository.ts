import { CustomerRemoteDataSource } from '../remote/CustomerRemoteDataSource';
import { CustomerLocalDataSource } from '../local/CustomerLocalDataSource';
import { CustomerMapper } from '../mappers/CustomerMapper';
import type { CustomerProfile } from '../../domain/entities/CustomerProfile';
import { Logger } from '../../core/observability/logger';
import type { ICustomerRepository } from '../../domain/repositories/ICustomerRepository';

export class CustomerRepository implements ICustomerRepository {
  constructor(
    private remoteDataSource: CustomerRemoteDataSource,
    private localDataSource: CustomerLocalDataSource
  ) {}

  async getCustomerProfile(customerId: string): Promise<CustomerProfile> {
    try {
      const dto = await this.remoteDataSource.getCustomerProfile(customerId);
      return CustomerMapper.toDomain(dto);
    } catch (error) {
      Logger.warn(`Backend unavailable for Customer ${customerId}. Falling back to local data source.`, { error });
      const fallbackDto = await this.localDataSource.getCustomerProfile(customerId);
      return CustomerMapper.toDomain(fallbackDto);
    }
  }
}
