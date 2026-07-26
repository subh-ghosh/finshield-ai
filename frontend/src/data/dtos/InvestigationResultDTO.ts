export interface AgentTimelineEntry {
  timestamp: string;
  tool: string;
  duration: number;
  result: string;
  status: 'WAITING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
}

export interface EvidenceGraphLayer {
  name: string;
  count: number;
  items: { source: string; description: string }[];
}

export interface EvidenceGraph {
  layers: EvidenceGraphLayer[];
  attribution: {
    rule_pct: number;
    ml_pct: number;
    graph_pct: number;
    compliance_pct: number;
  };
}

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
  /** V2: agent execution trace from LangGraph */
  planner_timeline?: AgentTimelineEntry[];
  /** V2: structured evidence graph from evidence_aggregator */
  evidence_graph?: EvidenceGraph;
}
