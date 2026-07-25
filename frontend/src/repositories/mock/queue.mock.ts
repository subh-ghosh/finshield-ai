import type { QueueItem } from "../../types";

export class MockQueueRepository {
  async getInvestigationQueue(): Promise<QueueItem[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));

    return [
      { id: "CUST-8392", customer: "Acme Corp Ltd", riskScore: 92, priority: "Critical", status: "Open", assignedTo: "Unassigned", lastUpdated: "2026-07-25" },
      { id: "CUST-1042", customer: "Global Traders Inc", riskScore: 85, priority: "High", status: "In Progress", assignedTo: "Sarah Jenkins", lastUpdated: "2026-07-24" },
      { id: "CUST-4491", customer: "TechVentures LLC", riskScore: 78, priority: "High", status: "Open", assignedTo: "Unassigned", lastUpdated: "2026-07-24" },
      { id: "CUST-9921", customer: "Nexus Dynamics", riskScore: 65, priority: "Medium", status: "In Progress", assignedTo: "Michael Chen", lastUpdated: "2026-07-23" },
      { id: "CUST-3371", customer: "Pacific Holdings", riskScore: 91, priority: "Critical", status: "Open", assignedTo: "Unassigned", lastUpdated: "2026-07-25" },
      { id: "CUST-7782", customer: "Zenith Exports", riskScore: 72, priority: "High", status: "Pending Review", assignedTo: "Anna Müller", lastUpdated: "2026-07-22" },
    ];
  }
}
