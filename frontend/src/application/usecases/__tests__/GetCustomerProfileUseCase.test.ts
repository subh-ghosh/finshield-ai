import { describe, it, expect, vi } from 'vitest';
import { GetCustomerProfileUseCase } from '../GetCustomerProfileUseCase';
import type { ICustomerRepository } from '../../../domain/repositories/ICustomerRepository';
import type { CustomerProfile } from '../../../domain/entities/CustomerProfile';

describe('GetCustomerProfileUseCase', () => {
  it('should call getCustomerProfile on the repository and return the result', async () => {
    // Arrange
    const mockProfile: CustomerProfile = {
      id: 'C_123',
      name: 'John Doe',
      kyc_status: 'Active',
      risk_score: 50,
      onboarding_date: '2023-01-01',
      industry: 'Tech',
      jurisdiction: 'USA',
      connections: [],
      recent_transactions: []
    };

    const mockRepo: ICustomerRepository = {
      getCustomerProfile: vi.fn().mockResolvedValue(mockProfile)
    };

    const useCase = new GetCustomerProfileUseCase(mockRepo);

    // Act
    const result = await useCase.execute('C_123');

    // Assert
    expect(mockRepo.getCustomerProfile).toHaveBeenCalledWith('C_123');
    expect(mockRepo.getCustomerProfile).toHaveBeenCalledTimes(1);
    expect(result).toEqual(mockProfile);
  });
});
