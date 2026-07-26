# FinShield AI
**An Agentic AI-powered Anti-Money Laundering (AML) Investigation Platform**

---

## Problem Statement
**AI-Powered Suspicious Activity Detection (Problem Statement 1)**

Financial institutions are mandated by regulatory bodies (FinCEN, FATF, local authorities) to implement robust AML compliance programs. Traditional rule-based systems generate excessive false positives, overwhelming compliance teams. Meanwhile, sophisticated laundering techniques — structuring, smurfing, and layering — evade conventional detection.

FinShield AI solves this by acting as an **autonomous AI Investigation Partner**: it parses natural language queries, dynamically selects only the tools relevant to the query, and returns explainable, evidence-backed risk assessments with actionable escalation recommendations.

---

## Solution Approach

### Agentic Architecture
FinShield AI is built on a **LangGraph multi-node investigation graph** with conditional routing — not a fixed sequential pipeline. The agent:

1. **Parses user intent** from natural language using an LLM (Gemini), extracting the customer ID, AML pattern type, and scope
2. **Dynamically builds an execution plan** — selects only the tools needed for the specific query
3. **Executes tools in sequence**, reasoning after each tool output
4. **Conditionally loops** back for more evidence or routes to final report generation
5. **Returns a structured investigation report** with risk score, evidence, explanation, and escalation recommendation

### Agent Graph Topology
```
START -> planner_node -> analysis_node -> reasoning_node -> decision_node
                              ^                                    |
                              +-- [needs more tools] -------------+
                                                                  |
                                              [sufficient] -> report_node -> END
```

### Multi-Agent Swarm (Backend)
9 specialized agents form the full AML analysis pipeline:
- **Customer Agent**: KYC profile, risk history, jurisdiction
- **Transaction Agent**: Velocity, rolling sums, temporal patterns
- **Network Agent**: Graph analysis, connectivity risk
- **Rule Intelligence Agent**: Deterministic AML rules (structuring, high-risk jurisdiction, rapid cash-out)
- **ML Intelligence Agent**: Isolation Forest anomaly scoring
- **GNN Agent**: TemporalGCN relational risk scoring across the transaction graph
- **Compliance Agent**: Hybrid risk fusion (0.3xRule + 0.3xML + 0.4xGNN)
- **Evidence Aggregator**: Structured evidence graph with attribution percentages
- **Audit Agent**: Immutable audit trail for regulatory compliance

### AML Detection Techniques
| Technique | Implementation |
|-----------|----------------|
| Structuring / Smurfing | Rule-004: Multiple transactions just below reporting threshold |
| High-Risk Jurisdiction | Rule-012: Cross-border to FATF grey-list countries |
| Rapid Cash-Out | Rule-008: High-velocity cash withdrawals |
| Isolation Forest | Unsupervised anomaly detection on engineered customer features |
| Graph Neural Network | TemporalGCN detects relational risk across transaction graph |
| Counterfactual Simulation | "What-if" analysis predicting risk changes before they happen |

---

## Dataset Information

### Dataset: IBM AML Simulation Dataset
**Source**: IBM Research — publicly available on Kaggle  
**URL**: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml  
**License**: Community Data License Agreement - Sharing - Version 1.0

**Location in repo**: `dataset/` folder

### Files

| File | Rows | Description |
|------|------|-------------|
| `dataset/transactions.csv` | 1,323,234 | All financial transactions |
| `dataset/accounts.csv` | ~10,000 | Account and customer metadata |
| `dataset/alerts.csv` | 1,719+ | Known suspicious alert events |

### Schema — transactions.csv

| Column | Type | Description |
|--------|------|-------------|
| `TX_ID` | int | Unique transaction ID |
| `SENDER_ACCOUNT_ID` | int | Sending account identifier |
| `RECEIVER_ACCOUNT_ID` | int | Receiving account identifier |
| `TX_TYPE` | string | Transaction type (e.g., TRANSFER) |
| `TX_AMOUNT` | float | Transaction amount (USD) |
| `TIMESTAMP` | int | Simulation step (time unit) |
| `IS_FRAUD` | bool | Ground truth AML label |
| `ALERT_ID` | int | Alert ID (-1 if no alert) |

### Schema — accounts.csv

| Column | Type | Description |
|--------|------|-------------|
| `ACCOUNT_ID` | int | Unique account identifier |
| `CUSTOMER_ID` | string | Customer identifier (e.g., C_1) |
| `INIT_BALANCE` | float | Initial account balance |
| `COUNTRY` | string | Account country (ISO code) |
| `ACCOUNT_TYPE` | string | Account type classification |
| `IS_FRAUD` | bool | Whether this account is a fraudulent actor |
| `TX_BEHAVIOR_ID` | int | Transaction behavior profile ID |

### Dataset Statistics
- **Total transactions**: 1,323,234
- **Fraudulent transactions**: 1,719 (0.13% — highly imbalanced, realistic)
- **Alert types in alerts.csv**: fan_in, fan_out, cycle, scatter_gather, etc.
- **AML patterns covered**: Fan-in, Fan-out, Cycle, Scatter-gather, Bipartite

### How the Pipeline Uses This Dataset
1. `transactions.csv` is loaded and mapped to canonical columns via `SchemaMapper`
2. Joined with `accounts.csv` to enrich with `CUSTOMER_ID` and `COUNTRY`
3. Features engineered: velocity, rolling sums, amount deviation, cross-account flows
4. `IS_FRAUD` column used as ground truth for model training/evaluation

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, react-force-graph-2d, Framer Motion |
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI Agent | LangGraph, LangChain, Google Gemini API (gemini-1.5-pro) |
| Machine Learning | scikit-learn (Isolation Forest), NumPy (custom TemporalGCN) |
| Rule Engine | Custom deterministic Python rule classes |
| Graph Analysis | NetworkX, custom Graph Neural Network (numpy-only) |
| State Management | React Query (TanStack) |
| Database | SQLite (local dev), PostgreSQL-compatible |

### External Tools, APIs & AI Assistance Disclosure
As required by hackathon rules:

| Tool | Usage |
|------|-------|
| **Google Gemini API** (gemini-1.5-pro) | LLM for agent intent parsing, reasoning, and report generation |
| **Antigravity (Google DeepMind)** | AI coding assistant used for scaffolding, implementation, and debugging |
| **LangGraph** | Open-source multi-agent orchestration framework |
| **LangChain** | Open-source LLM integration library |
| **scikit-learn** | Open-source ML library (Isolation Forest) |
| **react-force-graph-2d** | Open-source graph visualization library |
| **Framer Motion** | Open-source React animation library |

---

## Setup Instructions

### Prerequisites
- Python 3.11+ and Node.js 18+
- Google Gemini API key (free tier at [Google AI Studio](https://aistudio.google.com))

### 1. Clone the Repository
```bash
git clone https://github.com/subh-ghosh/finshield-ai.git
cd finshield-ai
```

### 2. Dataset
The IBM AML dataset is included in the `dataset/` folder:
- `dataset/transactions.csv` — 1.3M transactions
- `dataset/accounts.csv` — Account/customer metadata
- `dataset/alerts.csv` — Known suspicious alerts

> Source: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml

### 3. Backend Setup
```bash
python -m venv venv

# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r backend/requirements.txt

cp backend/.env.example backend/.env
# Edit backend/.env — set GEMINI_API_KEY=your_key_here

cd backend
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 5. Access
- **Frontend**: http://localhost:5173
- **Backend API / Docs**: http://localhost:8000/docs

> Note: On first startup, the backend will process the full 1.3M row dataset and cache results. This takes ~2-3 minutes. Subsequent startups use the cache instantly.

---

## Usage

### Natural Language Chat Mode
Navigate to a customer and type queries like:
```
"Analyse this dataset for suspicious activity"
"Find structuring patterns in the last 30 days"
"Which customers made 10+ transactions under $10,000?"
"Is customer C_1 suspicious?"
"Flag high-risk customers"
```
The agent dynamically selects only the relevant tools for each query.

### Enterprise Investigation Mode
Click **"Run Investigation"** on any customer to trigger the 9-agent swarm with:
- Live agent execution graph | Evidence consensus board | Counterfactual simulator
- AI rule suggestions | Case lifecycle management | Knowledge graph

### Key API Endpoints

**Core Agent Tool Endpoints** (the 5 tools the agent selects from):
| Endpoint | Method | Tool Name | Description |
|----------|--------|-----------|-------------|
| `/api/v1/eda/summary` | GET | `eda_analysis` | Dataset EDA: fraud rate, distributions, top risky customers |
| `/api/v1/features/{id}` | GET | `feature_engineering` | AML feature vector: velocity, structuring score, smurfing score, cash-out ratio |
| `/api/v1/anomaly/{id}` | GET | `anomaly_detection` | Isolation Forest score, prediction, severity, interpretation |
| `/api/v1/anomaly/summary/top` | GET | — | Top N most anomalous customers |
| `/api/v1/risk-classify/{id}` | GET | `risk_classification` | Hybrid risk score (0-100), category, escalation action |
| `/api/v1/risk-classify/summary/distribution` | GET | — | Risk category distribution across all customers |
| `/api/v1/explanation/{id}` | GET | `get_explanation` | Full Gemini-generated explanation with evidence timeline |

**Investigation & Pipeline Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/planner/investigate` | POST | Agentic investigation: parses query, selects tools, returns structured result |
| `/api/v1/analyze/customer` | POST | Single customer full pipeline analysis |
| `/api/v1/analyze/batch` | POST | Batch analyze multiple customers |
| `/api/v1/customer/{id}` | GET | Customer feature profile |
| `/api/v1/graph/ego/{id}` | GET | Knowledge graph for entity |
| `/api/v1/rules/suggestions` | GET | AI-suggested rules |
| `/api/v1/simulation/what-if` | POST | Counterfactual simulation |
| `/api/v1/monitoring/watchlist` | GET | Monitored customers |

---

## Project Structure
```
finshield-ai/
├── dataset/
│   ├── transactions.csv     <- IBM AML transactions (1.3M rows)
│   ├── accounts.csv         <- Account/customer metadata
│   └── alerts.csv           <- Known suspicious alerts
├── backend/app/
│   ├── agent/               <- Multi-agent swarm (LangGraph)
│   ├── planner/             <- Enterprise investigation planner
│   ├── ml/                  <- Isolation Forest, GNN, Hybrid Risk Engine
│   ├── rules/               <- Deterministic AML rule engine + rule suggester
│   ├── explainability/      <- Natural language explanation generation
│   └── api/v1/routers/      <- FastAPI REST endpoints
├── frontend/src/
│   ├── pages/               <- Dashboard, Investigation Workspace
│   └── components/          <- AgentSwarmView, KnowledgeGraph, etc.
└── docs/                    <- Architecture and design documents
```

---

## Data Sources

| Source | Type | URL | Usage |
|--------|------|-----|-------|
| **IBM AML Simulation Dataset** | **Primary** | https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml | Main transaction dataset (1.3M rows, 3 files) |
| FATF High-Risk Jurisdictions | Reference | https://www.fatf-gafi.org/en/topics/high-risk-and-other-monitored-jurisdictions.html | High-risk country list for Rule-012 |
| IBM AML Research Paper | Reference | https://arxiv.org/abs/2306.16272 | AML pattern taxonomy (fan-in, fan-out, cycle) |
