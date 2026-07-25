import { Repositories } from '../repositories';

export class QueueService {
  async getInvestigationQueue() {
    return await Repositories.queue.getInvestigationQueue();
  }
}

export const queueService = new QueueService();
