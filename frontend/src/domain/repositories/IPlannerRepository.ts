import type { InvestigationResult } from '../entities/InvestigationResult';

export interface IPlannerRepository {
  runInvestigation(customerId: string, request?: string): Promise<InvestigationResult>;
}
