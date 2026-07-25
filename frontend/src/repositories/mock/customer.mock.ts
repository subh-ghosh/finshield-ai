import type { Customer } from "../../types";

export class MockCustomerRepository {
  async getCustomerById(id: string): Promise<Customer> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 600));

    return {
      id,
      name: "Acme Corp Ltd",
      industry: "Import/Export",
      jurisdiction: "Cayman Islands",
      onboarding_date: "2023-01-15",
      kyc_status: "Active",
      risk_score: 92,
      historical_risk: "High",
      connections: [
        { id: "CUST-1042", name: "Global Traders Inc", role: "Shared Director", risk: "High" },
        { id: "CUST-5512", name: "Offshore Holdings", role: "Parent Company", risk: "Medium" }
      ],
      recent_transactions: [
        { date: "2026-07-24", amount: "$9,900.00", type: "Wire Transfer", status: "Completed", party: "Unknown Entity A" },
        { date: "2026-07-24", amount: "$9,950.00", type: "Wire Transfer", status: "Completed", party: "Unknown Entity B" },
        { date: "2026-07-23", amount: "$500,000.00", type: "Incoming Wire", status: "Completed", party: "Offshore Holdings" },
      ]
    };
  }
}
