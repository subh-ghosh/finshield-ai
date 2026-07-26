import type { AgentTimelineEntry, EvidenceGraph } from '../../data/dtos/InvestigationResultDTO';

export interface InvestigationResult {
  readonly customerId: string;
  readonly correlationId: string;
  readonly recommendation: 'CLEAR' | 'MANUAL_REVIEW' | 'ESCALATE' | 'FILE_SAR';
  readonly confidence: number;
  readonly finalReport: string;
  readonly toolCalls: number;
  readonly apiCalls: number;
  readonly executionTimeMs: number;
  readonly reasoningSteps: ReadonlyArray<{
    readonly step: string;
    readonly description: string;
    readonly timestamp?: string;
  }>;
  
  // Legacy / DTO Compatibility Fields expected by components
  readonly customer_id?: string;
  readonly correlation_id?: string;
  readonly planner_status?: string;
  readonly investigation_complete?: boolean;
  readonly final_report?: string;
  readonly tool_calls?: string[];
  readonly api_calls?: number;
  readonly execution_time_ms?: number;
  readonly reasoning_steps?: string[];
  readonly errors?: string[];

  // V2: multi-agent execution data
  readonly planner_timeline?: AgentTimelineEntry[];
  readonly evidence_graph?: EvidenceGraph;
}
