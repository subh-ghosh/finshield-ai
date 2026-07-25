export interface InvestigationResultDTO {
  customer_id: string;
  correlation_id: string;
  planner_status: string;
  investigation_complete: boolean;
  recommendation: string;
  confidence: string;
  final_report: string;
  tool_calls: string[];
  api_calls: number;
  reasoning_steps: string[];
  execution_time_ms: number;
  errors: string[];
}
