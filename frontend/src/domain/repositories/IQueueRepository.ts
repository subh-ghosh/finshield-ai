import type { QueueItem } from '../entities/QueueItem';

export interface IQueueRepository {
  getQueue(): Promise<QueueItem[]>;
}
