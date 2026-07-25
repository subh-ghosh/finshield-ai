export interface QueueItemDTO {
  id: string;
  customer: string;
  riskScore: number;
  priority: string;
  status: string;
  assignedTo: string;
  lastUpdated: string;
}
