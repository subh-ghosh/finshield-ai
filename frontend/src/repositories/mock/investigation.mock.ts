import type { Investigation } from "../../types";

export class MockInvestigationRepository {
  async getInvestigationById(id: string): Promise<Investigation> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 600));

    return {
      id,
      customer_id: id,
      status: 'In Progress',
      risk_profile: {
        composite_score: 92,
        ml_anomaly_score: 94,
        rule_base_score: 88,
      },
      evidences: [
        { id: 1, title: 'Velocity Anomaly Detected', desc: 'Transaction frequency is 400% above baseline.', severity: 'critical', confidence: 0.96, source: 'Isolation Forest' },
        { id: 2, title: 'Structuring Pattern', desc: 'Multiple transactions just below reporting threshold.', severity: 'critical', confidence: 0.89, source: 'Rule Engine' },
        { id: 3, title: 'Jurisdiction Risk', desc: 'Entity located in Cayman Islands.', severity: 'medium', confidence: 1.0, source: 'KYC System' }
      ],
      rule_results: [
        { rule_id: 'VELOCITY_001', description: 'Transaction frequency anomaly', triggered: true, score_contribution: 35 },
        { rule_id: 'STRUCTURING_002', description: 'Multiple transfers under $10k', triggered: true, score_contribution: 45 }
      ],
      recommendation: {
        action: 'SAR',
        reasoning: 'Critical velocity anomaly combined with clear structuring patterns warrants immediate SAR filing.'
      }
    };
  }
}
