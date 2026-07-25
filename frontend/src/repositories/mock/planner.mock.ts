import type { PlannerEvent } from "../../types";

export class MockPlannerRepository {
  async sendMessage(
    _message: string,
    onEvent: (event: PlannerEvent) => void
  ): Promise<void> {
    return new Promise((resolve) => {
      // Simulate Planner streaming response
      setTimeout(() => onEvent({ type: 'tool_start', content: '', step: { id: 's1', tool_name: 'query_transactions', status: 'running', timestamp: new Date().toISOString() } }), 500);
      
      setTimeout(() => onEvent({ type: 'tool_end', content: '', step: { id: 's1', tool_name: 'query_transactions', status: 'completed', timestamp: new Date().toISOString(), duration_ms: 450, output: 'Found 145 transactions' } }), 1500);
      
      setTimeout(() => onEvent({ type: 'tool_start', content: '', step: { id: 's2', tool_name: 'run_hybrid_risk', status: 'running', timestamp: new Date().toISOString() } }), 2000);
      
      setTimeout(() => onEvent({ type: 'tool_end', content: '', step: { id: 's2', tool_name: 'run_hybrid_risk', status: 'completed', timestamp: new Date().toISOString(), duration_ms: 600, output: 'Risk Score: 92 (Critical)' } }), 3000);

      setTimeout(() => {
        onEvent({ type: 'final_answer', content: 'Based on the transaction history and hybrid risk score, this entity presents a critical risk. Velocity is 400% above normal and there are structuring indicators.' });
        resolve();
      }, 4000);
    });
  }
}
