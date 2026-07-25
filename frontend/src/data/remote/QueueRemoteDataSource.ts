import { api } from '../../core/api';
import type { QueueItemDTO } from '../dtos/QueueItemDTO';

export class QueueRemoteDataSource {
  async getQueue(): Promise<QueueItemDTO[]> {
    // This API does not exist yet. It's documented as Tech Debt.
    const response = await api.get<QueueItemDTO[]>('/v1/queue');
    return response.data;
  }
}
