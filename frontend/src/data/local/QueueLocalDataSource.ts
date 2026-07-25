import type { QueueItemDTO } from '../dtos/QueueItemDTO';

export class QueueLocalDataSource {
  async getQueue(): Promise<QueueItemDTO[]> {
    return [
      { customer_id: "C_8392", customer_name: "Acme Corp Ltd", risk_score: 92, priority: "Critical", status: "Open", assigned_to: "Unassigned", last_updated: "2026-07-25" },
      { customer_id: "C_1042", customer_name: "Global Traders Inc", risk_score: 85, priority: "High", status: "In Progress", assigned_to: "Sarah Jenkins", last_updated: "2026-07-24" },
      { customer_id: "C_4491", customer_name: "TechVentures LLC", risk_score: 78, priority: "High", status: "Open", assigned_to: "Unassigned", last_updated: "2026-07-24" },
      { customer_id: "C_9921", customer_name: "Nexus Dynamics", risk_score: 65, priority: "Medium", status: "In Progress", assigned_to: "Michael Chen", last_updated: "2026-07-23" },
      { customer_id: "C_3371", customer_name: "Pacific Holdings", risk_score: 91, priority: "Critical", status: "Open", assigned_to: "Unassigned", last_updated: "2026-07-25" },
      { customer_id: "C_7782", customer_name: "Zenith Exports", risk_score: 72, priority: "High", status: "Pending Review", assigned_to: "Anna Müller", last_updated: "2026-07-22" },
    ];
  }
}
