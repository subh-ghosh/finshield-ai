import type { InvestigationResult } from '../entities/InvestigationResult';

export interface IPlannerRepository {
  runInvestigation(customerId: string): Promise<InvestigationResult>;
}
