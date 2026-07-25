import type { InvestigationResultDTO } from '../dtos/InvestigationResultDTO';

export class PlannerLocalDataSource {
  async runInvestigation(customerId: string): Promise<InvestigationResultDTO> {
    return {
      customer_id: customerId,
      correlation_id: `INV-${Date.now()}`,
      recommendation: 'MANUAL_REVIEW',
      confidence: 0.85,
      final_report: 'This is a mocked fallback investigation report. Backend API is currently unavailable.',
      tool_calls: 3,
      api_calls: 5,
      execution_time_ms: 1500,
      reasoning_steps: [
        {
          action: 'Initializing fallback',
          description: 'Loaded offline fallback data.',
          timestamp: new Date().toISOString(),
        }
      ]
    };
  }
}
