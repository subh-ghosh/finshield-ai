import type { DashboardData } from "../../types";

export class MockDashboardRepository {
  async getDashboardData(): Promise<DashboardData> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));

    return {
      metrics: {
        activeInvestigations: 124,
        highRiskEntities: 38,
        newAlerts: 15,
        pendingReviews: 42
      },
      riskDistribution: [
        { name: "Low", value: 450, color: "#94A3B8" },
        { name: "Medium", value: 320, color: "#F59E0B" },
        { name: "High", value: 150, color: "#EF4444" },
        { name: "Critical", value: 38, color: "#E1000F" }
      ],
      anomalyTrend: [
        { time: "00:00", score: 12 },
        { time: "04:00", score: 8 },
        { time: "08:00", score: 35 },
        { time: "12:00", score: 42 },
        { time: "16:00", score: 38 },
        { time: "20:00", score: 15 },
      ]
    };
  }
}
