import { Repositories } from '../repositories';

export class DashboardService {
  async getDashboardData() {
    return await Repositories.dashboard.getDashboardData();
  }
}

export const dashboardService = new DashboardService();
