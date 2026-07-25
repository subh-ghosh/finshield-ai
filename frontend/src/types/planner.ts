export type ExecutionStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface ExecutionStep {
  id: string;
  tool_name: string;
  status: ExecutionStatus;
  timestamp: string;
  duration_ms?: number;
  input?: string;
  output?: string;
  error?: string;
}

export interface PlannerEvent {
  type: 'thought' | 'tool_start' | 'tool_end' | 'error' | 'final_answer';
  content: string;
  step?: ExecutionStep;
}

export interface PlannerState {
  is_running: boolean;
  events: PlannerEvent[];
  current_step?: ExecutionStep;
  final_answer?: string;
  error?: string;
}

export interface PlannerResult {
  customer_id: string;
  planner_status: string;
  investigation_complete: boolean;
  recommendation: string;
  confidence: string;
  final_report?: string;
  tool_calls: string[];
  api_calls: number;
  reasoning_steps: string[];
  execution_time_ms: number;
  errors: string[];
  correlation_id: string;
}
