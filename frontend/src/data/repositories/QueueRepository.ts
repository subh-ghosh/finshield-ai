import { QueueRemoteDataSource } from '../remote/QueueRemoteDataSource';
import { QueueLocalDataSource } from '../local/QueueLocalDataSource';
import { QueueMapper } from '../mappers/QueueMapper';
import type { QueueItem } from '../../domain/entities/QueueItem';
import type { IQueueRepository } from '../../domain/repositories/IQueueRepository';
import { Logger } from '../../core/observability/logger';

export class QueueRepository implements IQueueRepository {
  constructor(
    private remoteDataSource: QueueRemoteDataSource,
    private localDataSource: QueueLocalDataSource
  ) {}

  async getQueue(): Promise<QueueItem[]> {
    const dtos = await this.remoteDataSource.getQueue();
    return dtos.map(dto => QueueMapper.toDomain(dto));
  }
}
