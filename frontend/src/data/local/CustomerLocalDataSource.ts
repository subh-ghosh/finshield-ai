import type { CustomerProfileDTO } from '../dtos/CustomerProfileDTO';

export class CustomerLocalDataSource {
  async getCustomerProfile(customerId: string): Promise<CustomerProfileDTO> {
    return {
      customer_id: customerId,
      feature_metrics: {
        customer_id: customerId,
        transaction_count: 25,
        total_amount: 112117320.0,
        average_amount: 4484693.0,
        maximum_amount: 21474836.0,
        minimum_amount: 2392.47,
        velocity_score: 0.0,
        structuring_score: 0.0,
        smurfing_score: 0.0,
        recipient_diversity: 0.0,
        sender_diversity: 0.0,
        cash_in_ratio: 0.0,
        cash_out_ratio: 0.0,
        night_transaction_ratio: 0.0,
        weekend_transaction_ratio: 0.0,
        round_amount_ratio: 0.0,
        rolling_amount_24h: 0.0,
        rolling_count_24h: 0,
        days_since_last_transaction: 0.0,
        account_age: 0.0,
        risk_score_placeholder: 0.0,
      },
      rule_summary: {
        score: 15,
        severity: "LOW",
        triggered_count: 1
      },
      anomaly_summary: {
        anomaly_score: 0.519,
        severity: "MEDIUM",
        confidence: 0.039
      }
    };
  }
}
