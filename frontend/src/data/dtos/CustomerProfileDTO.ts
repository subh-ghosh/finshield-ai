export interface CustomerProfileDTO {
  customer_id: string;
  feature_metrics: {
    customer_id: string;
    transaction_count: number;
    total_amount: number;
    average_amount: number;
    maximum_amount: number;
    minimum_amount: number;
    velocity_score: number;
    structuring_score: number;
    smurfing_score: number;
    recipient_diversity: number;
    sender_diversity: number;
    cash_in_ratio: number;
    cash_out_ratio: number;
    night_transaction_ratio: number;
    weekend_transaction_ratio: number;
    round_amount_ratio: number;
    rolling_amount_24h: number;
    rolling_count_24h: number;
    days_since_last_transaction: number;
    account_age: number;
    risk_score_placeholder: number;
  };
  rule_summary: {
    score: number;
    severity: string;
    triggered_count: number;
  };
  anomaly_summary: {
    anomaly_score: number;
    severity: string;
    confidence: number;
  };
}
