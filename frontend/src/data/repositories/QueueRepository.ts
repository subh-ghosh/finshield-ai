import { QueueRemoteDataSource } from '../remote/QueueRemoteDataSource';
import { QueueLocalDataSource } from '../local/QueueLocalDataSource';
import { QueueMapper } from '../mappers/QueueMapper';
import type { QueueItem } from '../../domain/entities/QueueItem';
import type { IQueueRepository } from '../../domain/repositories/IQueueRepository';

export class QueueRepository implements IQueueRepository {
  constructor(
    private remoteDataSource: QueueRemoteDataSource,
    private localDataSource: QueueLocalDataSource
  ) {}

  async getQueue(): Promise<QueueItem[]> {
    try {
      const dtos = await this.remoteDataSource.getQueue();
      return dtos.map(dto => QueueMapper.toDomain(dto));
    } catch (error) {
      Logger.warn('Backend unavailable for Queue. Falling back to local data source.', { error });
      const fallbackDtos = await this.localDataSource.getQueue();
      return fallbackDtos.map(dto => QueueMapper.toDomain(dto));
    }
  }
}
