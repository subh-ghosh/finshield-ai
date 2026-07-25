import type { IPlannerRepository } from '../../domain/repositories/IPlannerRepository';
import type { InvestigationResult } from '../../domain/entities/InvestigationResult';

export class RunInvestigationUseCase {
  constructor(private plannerRepository: IPlannerRepository) {}

  async execute(customerId: string): Promise<InvestigationResult> {
    return this.plannerRepository.runInvestigation(customerId);
  }
}
