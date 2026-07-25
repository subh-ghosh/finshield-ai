import { Repositories } from '../repositories';
import type { PlannerEvent } from "../types";

export class PlannerService {
  async sendMessage(message: string, onEvent: (event: PlannerEvent) => void) {
    if (!message.trim()) throw new Error('Message cannot be empty');
    return await Repositories.planner.sendMessage(message, onEvent);
  }
}

export const plannerService = new PlannerService();
