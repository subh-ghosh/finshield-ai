import { MockDashboardRepository } from './mock/dashboard.mock';
import { MockQueueRepository } from './mock/queue.mock';
import { MockCustomerRepository } from './mock/customer.mock';
import { MockInvestigationRepository } from './mock/investigation.mock';
import { MockPlannerRepository } from './mock/planner.mock';

export const Repositories = {
  dashboard: new MockDashboardRepository(),
  queue: new MockQueueRepository(),
  customer: new MockCustomerRepository(),
  investigation: new MockInvestigationRepository(),
  planner: new MockPlannerRepository(),
};
