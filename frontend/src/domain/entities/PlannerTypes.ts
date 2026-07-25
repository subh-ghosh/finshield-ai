export interface Evidence {
  readonly title: string;
  readonly description: string;
  readonly source: string;
  readonly type: 'transaction' | 'connection' | 'historical' | 'rule' | 'anomaly';
  readonly risk_level: 'High' | 'Medium' | 'Low';
}

export interface ExecutionStep {
  readonly id: string;
  readonly message: string;
  readonly status: 'pending' | 'running' | 'completed' | 'error';
  readonly duration?: string;
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
