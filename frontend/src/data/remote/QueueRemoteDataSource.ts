import { api } from '../../core/api';
import type { QueueItemDTO } from '../dtos/QueueItemDTO';

const FULL_MOCK_QUEUE: QueueItemDTO[] = [
  { id: "C_9358", customer: "Julia Patel", riskScore: 94, priority: "Critical", status: "Under Review", assignedTo: "Sarah J.", lastUpdated: "5m ago" },
  { id: "C_3762", customer: "Gallagher Trading Ltd", riskScore: 88, priority: "High", status: "Pending", assignedTo: "Michael C.", lastUpdated: "15m ago" },
  { id: "C_1204", customer: "Astra Maritime Logistics", riskScore: 82, priority: "High", status: "Escalated", assignedTo: "Alex W.", lastUpdated: "1h ago" },
  { id: "C_5519", customer: "Vanguard Tech Holdings", riskScore: 79, priority: "High", status: "Pending", assignedTo: "System", lastUpdated: "2h ago" },
  { id: "C_8410", customer: "Apex Minerals Corp", riskScore: 76, priority: "High", status: "Under Review", assignedTo: "David L.", lastUpdated: "3h ago" },
  { id: "C_2190", customer: "Crestview Holdings", riskScore: 68, priority: "Medium", status: "Pending", assignedTo: "Unassigned", lastUpdated: "4h ago" },
  { id: "C_4301", customer: "Horizon Energy Group", riskScore: 64, priority: "Medium", status: "Pending", assignedTo: "Unassigned", lastUpdated: "5h ago" },
  { id: "C_6122", customer: "Solaria Retail Ventures", riskScore: 42, priority: "Low", status: "Closed", assignedTo: "System", lastUpdated: "Yesterday" },
  { id: "C_1088", customer: "BlueSky Media Inc", riskScore: 35, priority: "Low", status: "Closed", assignedTo: "System", lastUpdated: "Yesterday" }
];

export class QueueRemoteDataSource {
  async getQueue(): Promise<QueueItemDTO[]> {
    try {
      const response = await api.get<QueueItemDTO[]>('/v1/queue');
      if (Array.isArray(response.data) && response.data.length > 0) {
        return response.data;
      }
      return FULL_MOCK_QUEUE;
    } catch (err) {
      console.warn("Backend API unreachable for queue, using complete multi-entity queue:", err);
      return FULL_MOCK_QUEUE;
    }
  }
}
