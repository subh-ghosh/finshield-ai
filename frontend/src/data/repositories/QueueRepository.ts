import { QueueRemoteDataSource } from '../remote/QueueRemoteDataSource';

import { QueueMapper } from '../mappers/QueueMapper';
import type { QueueItem } from '../../domain/entities/QueueItem';
import type { IQueueRepository } from '../../domain/repositories/IQueueRepository';

export class QueueRepository implements IQueueRepository {
  constructor(
    private remoteDataSource: QueueRemoteDataSource
  ) {}

  async getQueue(): Promise<QueueItem[]> {
    const dtos = await this.remoteDataSource.getQueue();
    return dtos.map(dto => QueueMapper.toDomain(dto));
  }
}
