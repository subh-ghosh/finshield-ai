export interface QueueItem {
  id: string;
  customer: string;
  riskScore: number;
  status: 'Open' | 'In Progress' | 'Pending Review' | 'Closed';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  assignedTo?: string;
  lastUpdated: string;
}
