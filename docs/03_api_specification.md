# API Specification

FinShield AI uses a RESTful API architecture powered by FastAPI.

## Base URL
`/api/v1`

## 1. Authentication APIs
*(Mocked for Hackathon)*
- `POST /auth/login`: Authenticate and return JWT.

## 2. Investigation Management
- `POST /investigations`: Create a new investigation case.
- `GET /investigations`: List active investigations for the dashboard.
- `GET /investigations/{id}`: Retrieve full case details.
- `PUT /investigations/{id}/status`: Update case status (e.g., OPEN, PENDING_REVIEW, CLOSED).

## 3. Customer360 APIs
- `GET /customers/{id}`: Retrieve unified customer profile, KYC status, and risk rating.
- `GET /customers/{id}/accounts`: Retrieve linked accounts.

## 4. Transaction APIs
- `GET /customers/{id}/transactions`: Retrieve transaction history with pagination and filtering.
- `GET /transactions/timeline`: Retrieve aggregated chronological transactions for visualization.

## 5. Agentic AI APIs (The Core)
This is the primary interaction point for the chat/planner interface.

### `POST /ai/planner`
**Description**: Submits a natural language query or structured intent to the AI Planner. The Planner evaluates the request, selects tools, executes them, and returns an explainable recommendation.

**Request**:
```json
{
  "investigationId": "INV1001",
  "query": "Find structuring patterns in the last 30 days for this customer"
}
```

**Response**:
```json
{
  "status": "SUCCESS",
  "plan_executed": [
    "Apply Time Filter",
    "Run Feature Engineering (Structuring)",
    "Run Anomaly Detection",
    "Generate Explanation"
  ],
  "recommendation": "High Risk",
  "evidence": [
    "15 transfers just below the $10,000 reporting threshold.",
    "Velocity is 9x higher than normal."
  ],
  "explanation": "The customer exhibits a classic structuring (smurfing) pattern, breaking down large deposits into smaller chunks over a 30-day period.",
  "suggested_action": "Flag for review and file SAR."
}
```
