import { DashboardRemoteDataSource } from '../data/remote/DashboardRemoteDataSource';
import { DashboardLocalDataSource } from '../data/local/DashboardLocalDataSource';
import { DashboardRepository } from '../data/repositories/DashboardRepository';
import { GetDashboardMetricsUseCase } from '../application/usecases/GetDashboardMetricsUseCase';

import { CustomerRemoteDataSource } from '../data/remote/CustomerRemoteDataSource';
import { CustomerLocalDataSource } from '../data/local/CustomerLocalDataSource';
import { CustomerRepository } from '../data/repositories/CustomerRepository';
import { GetCustomerProfileUseCase } from '../application/usecases/GetCustomerProfileUseCase';

import { PlannerRemoteDataSource } from '../data/remote/PlannerRemoteDataSource';
import { PlannerLocalDataSource } from '../data/local/PlannerLocalDataSource';
import { PlannerRepository } from '../data/repositories/PlannerRepository';
import { RunInvestigationUseCase } from '../application/usecases/RunInvestigationUseCase';

import { QueueRemoteDataSource } from '../data/remote/QueueRemoteDataSource';
import { QueueLocalDataSource } from '../data/local/QueueLocalDataSource';
import { QueueRepository } from '../data/repositories/QueueRepository';
import { GetQueueUseCase } from '../application/usecases/GetQueueUseCase';

// Instantiate Repositories
const dashboardRepository = new DashboardRepository(new DashboardRemoteDataSource(), new DashboardLocalDataSource());
const customerRepository = new CustomerRepository(new CustomerRemoteDataSource(), new CustomerLocalDataSource());
const plannerRepository = new PlannerRepository(new PlannerRemoteDataSource(), new PlannerLocalDataSource());
const queueRepository = new QueueRepository(new QueueRemoteDataSource(), new QueueLocalDataSource());

// Export Use Cases injected with Repositories
export const UseCases = {
  getDashboardMetrics: new GetDashboardMetricsUseCase(dashboardRepository),
  getCustomerProfile: new GetCustomerProfileUseCase(customerRepository),
  runInvestigation: new RunInvestigationUseCase(plannerRepository),
  getQueue: new GetQueueUseCase(queueRepository),
};
