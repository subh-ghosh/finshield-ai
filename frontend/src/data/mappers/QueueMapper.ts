import type { QueueItemDTO } from '../dtos/QueueItemDTO';
import type { QueueItem } from '../../domain/entities/QueueItem';

export class QueueMapper {
  static toDomain(dto: QueueItemDTO): QueueItem {
    return {
      id: dto.id,
      customer: dto.customer,
      riskScore: dto.riskScore,
      priority: dto.priority as any,
      status: dto.status as any,
      assignedTo: dto.assignedTo,
      lastUpdated: dto.lastUpdated,
    };
  }
}
