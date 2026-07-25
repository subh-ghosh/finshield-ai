import { api } from '../lib/api';
import { Repositories } from '../repositories';
import type { PlannerEvent } from "../types";

export class PlannerService {
  async sendMessage(message: string, onEvent: (event: PlannerEvent) => void) {
    if (!message.trim()) throw new Error('Message cannot be empty');
    return await Repositories.planner.sendMessage(message, onEvent);
  }

  async runInvestigation(customerId: string): Promise<any> {
    const response = await api.post('/v1/planner/investigate', { customer_id: customerId });
    return response.data;
  }

  async getHealth(): Promise<any> {
    const response = await api.get('/v1/health');
    return response.data;
  }

  async getVersion(): Promise<any> {
    const response = await api.get('/v1/version');
    return response.data;
  }
}

export const plannerService = new PlannerService();
