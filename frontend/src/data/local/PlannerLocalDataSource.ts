import type { InvestigationResultDTO } from '../dtos/InvestigationResultDTO';

export class PlannerLocalDataSource {
  async runInvestigation(customerId: string, request?: string): Promise<InvestigationResultDTO> {
    return {
      customer_id: customerId,
      correlation_id: `INV-${Date.now()}`,
      planner_status: 'FALLBACK',
      investigation_complete: true,
      recommendation: 'MANUAL_REVIEW',
      confidence: '0.85',
      final_report: `Fallback investigation report. Backend API is unavailable. Request: ${request || 'standard investigation'}.`,
      tool_calls: ['FallbackPlanner'],
      api_calls: 0,
      execution_time_ms: 1500,
      reasoning_steps: ['Initializing fallback: loaded offline investigation data.'],
      errors: []
    };
  }
}
