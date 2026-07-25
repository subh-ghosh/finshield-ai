import { Repositories } from '../repositories';

export class CustomerService {
  async getCustomerById(id: string) {
    if (!id) throw new Error('Customer ID is required');
    return await Repositories.customer.getCustomerById(id);
  }
}

export const customerService = new CustomerService();
