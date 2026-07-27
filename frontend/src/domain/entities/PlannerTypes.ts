export interface Evidence {
  readonly title: string;
  readonly description: string;
  readonly desc?: string;
  readonly source: string;
  readonly timestamp?: string;
  readonly confidence?: number;
  readonly severity?: 'critical' | 'high' | 'medium' | 'low';
  readonly type: 'transaction' | 'connection' | 'historical' | 'rule' | 'anomaly';
  readonly risk_level: 'High' | 'Medium' | 'Low';
}

export interface ExecutionStep {
  readonly id: string;
  readonly message: string;
  readonly tool_name?: string;
  readonly output?: string;
  readonly error?: string;
  readonly status: 'pending' | 'running' | 'completed' | 'error' | 'failed';
  readonly duration?: string;
  readonly duration_ms?: number;
  readonly evidence?: ReadonlyArray<Evidence>;
}

export interface PlannerEvent {
  readonly step: ExecutionStep;
}

export interface PlannerState {
  readonly is_running: boolean;
  readonly events: ReadonlyArray<PlannerEvent>;
  readonly current_step: string | null;
  readonly final_answer: string | null;
  readonly error: string | null;
}
