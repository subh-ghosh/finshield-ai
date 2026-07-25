import type { IQueueRepository } from '../../domain/repositories/IQueueRepository';
import type { QueueItem } from '../../domain/entities/QueueItem';

export class GetQueueUseCase {
  constructor(private queueRepository: IQueueRepository) {}

  async execute(): Promise<QueueItem[]> {
    return this.queueRepository.getQueue();
  }
}
