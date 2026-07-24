# Functional Requirements & Use Cases

## Key Use Cases (MVP)

### UC-1: Dashboard Overview
- The Analyst logs in and views a dashboard of active investigations, priority queues, and basic performance metrics.

### UC-2: Investigate Customer
- The Analyst selects a customer flagged by the legacy monitoring system.
- The system opens the **Investigation Workspace** displaying the Customer360 profile.

### UC-3: Agentic Querying (The Core Hackathon Feature)
- The Analyst inputs a natural language query into the AI prompt (e.g., "Is this customer engaging in structuring?").
- The **AI Planner** parses the query, decides which tools to run, executes them, and returns an Evidence Panel.

### UC-4: Review AI Explanation
- The Analyst reviews the AI's generated explanation and the specific transactions/features it flagged.
- The Analyst can view the "Planner Trace" to see exactly which steps the AI took to reach its conclusion.

### UC-5: Generate & Submit Report
- Based on the AI's findings and the Analyst's own judgment, a final report is generated.
- The Analyst submits the investigation for Manager Approval (Human-in-the-Loop).

## UI/UX Requirements
- **Premium Aesthetics**: Dark theme, glassmorphic cards, modern typography (Inter/Outfit).
- **Interactive Visuals**: Animated charts for transaction velocity and anomaly scores.
- **Evidence Board**: A clear, bulleted list of "Why" a customer is flagged, replacing black-box scores.
- **Execution Graph**: A visual representation of the Planner's thought process (e.g., highlighting which tools are currently running).
