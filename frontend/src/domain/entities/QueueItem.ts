export interface QueueItem {
  readonly id: string;
  readonly customer: string;
  readonly riskScore: number;
  readonly priority: 'Critical' | 'High' | 'Medium' | 'Low';
  readonly status: 'Open' | 'In Progress' | 'Pending Review';
  readonly assignedTo: string;
  readonly lastUpdated: string;
}
