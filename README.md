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
- **GNN Agent**: TemporalGCN relational risk scoring
- **Compliance Agent**: Hybrid risk fusion (0.3xRule + 0.3xML + 0.4xGNN)
- **Evidence Aggregator**: Structured evidence graph with attribution percentages
- **Audit Agent**: Immutable audit trail for regulatory compliance

### AML Detection Techniques
| Technique | Implementation |
|-----------|----------------|
| Structuring / Smurfing | Rule-004: Multiple transactions just below $10,000 threshold |
| High-Risk Jurisdiction | Rule-012: Cross-border to FATF grey-list countries |
| Rapid Cash-Out | Rule-008: High-velocity cash withdrawals |
| Isolation Forest | Unsupervised anomaly detection on engineered features |
| Graph Neural Network | TemporalGCN detects relational risk across transaction graph |
| Counterfactual Simulation | "What-if" analysis predicting risk before it happens |

---

## Dataset Information

### Dataset: Synthetic AML Transactions
**Type**: Synthetic — generated programmatically with documented logic (see `data/generate_dataset.py`)

**Inspiration / References**:
- PaySim Synthetic Financial Dataset — E. A. Lopez-Rojas, A. Elmir, S. Axelsson (2016) [Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1)
- IBM Transactions for Anti Money Laundering (AML) [Kaggle](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)

**File**: `data/aml_transactions.csv` | **Size**: 10,000 transactions, 500 customers

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | string | Unique transaction ID (e.g., TX_12345678) |
| `customer_id` | string | Sender customer ID (e.g., C_105707) |
| `recipient_id` | string | Recipient customer/entity ID |
| `amount` | float | Transaction amount in USD |
| `timestamp` | ISO-8601 | Transaction datetime (2024 calendar year) |
| `transaction_type` | enum | WIRE / CASH / ACH / CRYPTO / SWIFT |
| `country_origin` | ISO-3166 | Originating country code |
| `country_dest` | ISO-3166 | Destination country code |
| `ip_address` | string | Sender login IP address |
| `device_id` | string | Sender device fingerprint |
| `merchant_id` | string | Merchant ID (ACH transactions only) |
| `wallet_id` | string | Crypto wallet ID (CRYPTO transactions only) |
| `aml_pattern` | enum | Ground truth: NONE / STRUCTURING / SMURFING / LAYERING / SHELL |
| `is_flagged` | int | Ground truth label: 0 = clean, 1 = suspicious |

### Dataset Statistics
- **Total transactions**: 10,000 | **Flagged transactions**: ~1,024 (10.2%)
- **Flagged customers**: 50 out of 500 (10%)
- **AML patterns**: STRUCTURING (35%), SMURFING (25%), LAYERING (25%), SHELL (15%)
- **Date range**: 2024-01-01 to 2024-12-31
- **High-risk countries**: PK, YE, SY, IR, KP, MM, AF, HT, LA (FATF grey-list inspired)

### Synthetic Data Generation Logic
- **Clean transactions**: Random amounts ($100-$50,000), normal countries, realistic timestamps
- **Structuring**: Amounts $8,500-$9,999, CASH type, same origin/dest country
- **Smurfing**: Small amounts ($500-$3,000), many recipients from same source
- **Layering**: Large amounts ($20K-$200K), WIRE/SWIFT/CRYPTO through high-risk jurisdictions
- **Shell company**: Very large amounts ($50K-$500K), WIRE to shell entity IDs

To regenerate: `python data/generate_dataset.py`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, react-force-graph-2d, Framer Motion |
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI Agent | LangGraph, LangChain, Google Gemini API (gemini-1.5-pro) |
| Machine Learning | scikit-learn (Isolation Forest), NumPy (custom GCN) |
| Rule Engine | Custom deterministic Python rule classes |
| Graph Analysis | NetworkX, custom TemporalGCN (numpy-only) |
| State Management | React Query (TanStack) |
| Database | SQLite (local dev), PostgreSQL-compatible |

### External Tools, APIs & AI Assistance Disclosure
As required by hackathon rules:

| Tool | Usage |
|------|-------|
| **Google Gemini API** (gemini-1.5-pro) | LLM for agent intent parsing, reasoning, report generation |
| **Antigravity (Google DeepMind)** | AI coding assistant used for scaffolding, implementation, and debugging |
| **LangGraph** | Open-source multi-agent orchestration framework |
| **LangChain** | Open-source LLM integration library |
| **scikit-learn** | Open-source ML library (Isolation Forest) |
| **react-force-graph-2d** | Open-source graph visualization |
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

### 2. Backend Setup
```bash
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate

pip install -r backend/requirements.txt

cp backend/.env.example backend/.env
# Edit backend/.env — set GEMINI_API_KEY

python data/generate_dataset.py   # Generate synthetic dataset

cd backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Access
- **Frontend**: http://localhost:5173
- **Backend API / Docs**: http://localhost:8000/docs

---

## Usage

### Natural Language Chat Mode
Navigate to a customer and type queries like:
```
"Analyse this dataset for suspicious activity"
"Find structuring patterns in the last 30 days"
"Which customers made 10+ transactions under $10,000?"
"Is customer C_105707 suspicious?"
```
The agent dynamically selects only the relevant tools for each query.

### Enterprise Investigation Mode
Click **"Run Investigation"** on any customer to trigger the 9-agent swarm with:
- Live agent execution graph | Evidence consensus board | Counterfactual simulator
- AI rule suggestions | Case lifecycle management | Knowledge graph

### Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze/customer` | POST | Analyze a single customer |
| `/api/v1/analyze/batch` | POST | Batch analyze multiple customers |
| `/api/v1/explanation/{id}` | GET | Get full explanation report |
| `/api/v1/investigation/{id}` | POST | Run multi-agent investigation |
| `/api/v1/graph/ego/{id}` | GET | Knowledge graph for entity |
| `/api/v1/rules/suggestions` | GET | AI-suggested rules |
| `/api/v1/simulation/what-if` | POST | Counterfactual simulation |
| `/api/v1/monitoring/watchlist` | GET | Monitored customers |

---

## Project Structure
```
finshield-ai/
├── backend/app/
│   ├── agent/          <- Multi-agent swarm (LangGraph)
│   ├── planner/        <- Enterprise investigation planner
│   ├── ml/             <- Isolation Forest, GNN, Hybrid Risk Engine
│   ├── rules/          <- Deterministic AML rule engine + rule suggester
│   ├── explainability/ <- Natural language explanation generation
│   └── api/v1/routers/ <- FastAPI REST endpoints
├── frontend/src/
│   ├── pages/          <- Dashboard, Investigation Workspace
│   └── components/     <- AgentSwarmView, KnowledgeGraph, RuleSuggestionsWidget
├── data/
│   ├── generate_dataset.py  <- Synthetic data generator (documented)
│   └── aml_transactions.csv <- Generated dataset
└── docs/               <- Architecture and design documents
```

---

## Data Sources

| Source | Type | URL | Usage |
|--------|------|-----|-------|
| PaySim Synthetic Dataset | Reference/Inspiration | https://www.kaggle.com/datasets/ealaxi/paysim1 | Schema design, AML pattern definitions |
| IBM AML Transactions | Reference/Inspiration | https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml | AML pattern realism |
| FATF High-Risk Jurisdictions | Reference | https://www.fatf-gafi.org/en/topics/high-risk-and-other-monitored-jurisdictions.html | High-risk country list |
| **aml_transactions.csv** | **Primary (Synthetic)** | `data/` folder | Generated via `data/generate_dataset.py` |
