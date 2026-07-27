import type { QueueItemDTO } from '../dtos/QueueItemDTO';

export class QueueLocalDataSource {
  async getQueue(): Promise<QueueItemDTO[]> {
    return [
      { id: 'C_8392', customer: 'Acme Corp Ltd', riskScore: 92, priority: 'Critical', status: 'Open', assignedTo: 'Unassigned', lastUpdated: '2026-07-25' },
      { id: 'C_1042', customer: 'Global Traders Inc', riskScore: 85, priority: 'High', status: 'In Progress', assignedTo: 'Sarah Jenkins', lastUpdated: '2026-07-24' },
      { id: 'C_4491', customer: 'TechVentures LLC', riskScore: 78, priority: 'High', status: 'Open', assignedTo: 'Unassigned', lastUpdated: '2026-07-24' },
      { id: 'C_9921', customer: 'Nexus Dynamics', riskScore: 65, priority: 'Medium', status: 'In Progress', assignedTo: 'Michael Chen', lastUpdated: '2026-07-23' },
      { id: 'C_3371', customer: 'Pacific Holdings', riskScore: 91, priority: 'Critical', status: 'Open', assignedTo: 'Unassigned', lastUpdated: '2026-07-25' },
      { id: 'C_7782', customer: 'Zenith Exports', riskScore: 72, priority: 'High', status: 'Pending Review', assignedTo: 'Anna Muller', lastUpdated: '2026-07-22' },
    ];
  }
}
