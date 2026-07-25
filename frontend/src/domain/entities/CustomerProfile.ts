export interface CustomerProfile {
  readonly id: string;
  readonly name: string;
  readonly kyc_status: string;
  readonly risk_score: number;
  readonly onboarding_date: string;
  readonly industry: string;
  readonly jurisdiction: string;
  readonly historical_risk?: string;
  readonly connections: ReadonlyArray<{
    readonly id: string;
    readonly name: string;
    readonly role: string;
    readonly risk: 'Low' | 'Medium' | 'High' | 'Critical';
  }>;
  readonly recent_transactions: ReadonlyArray<{
    readonly date: string;
    readonly amount: string;
    readonly type: string;
    readonly status: string;
    readonly party: string;
  }>;
}
