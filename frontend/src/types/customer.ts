export interface CustomerConnection {
  id: string;
  name: string;
  role: string;
  risk: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface CustomerTransaction {
  date: string;
  amount: string;
  type: string;
  status: string;
  party: string;
}

export interface Customer {
  id: string;
  name: string;
  kyc_status: string;
  risk_score: number;
  onboarding_date: string;
  industry: string;
  jurisdiction: string;
  historical_risk?: string;
  connections: CustomerConnection[];
  recent_transactions: CustomerTransaction[];
}
