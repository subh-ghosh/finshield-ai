import { Repositories } from '../repositories';

export class InvestigationService {
  async getInvestigationById(id: string) {
    if (!id) throw new Error('Investigation ID is required');
    return await Repositories.investigation.getInvestigationById(id);
  }
}

export const investigationService = new InvestigationService();
