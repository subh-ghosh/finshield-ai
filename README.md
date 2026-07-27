# FinShield AI 🛡️
**An Enterprise Agentic AI-Powered Anti-Money Laundering (AML) Investigation Platform**

![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Orchestration-orange)
![Gemini AI](https://img.shields.io/badge/Gemini%202.5%20Flash-Generative%20AI-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![React](https://img.shields.io/badge/React%2BVite-Frontend-61DAFB)
![AML](https://img.shields.io/badge/AML-Compliance-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)

---

## 📖 Table of Contents
1. [Problem Statement](#-problem-statement)
2. [Our Solution](#-our-solution)
3. [Agentic Swarm Architecture](#-agentic-swarm-architecture)
4. [Dataset & Scale](#-dataset--scale)
5. [Tech Stack](#-tech-stack)
6. [Getting Started (Docker)](#-getting-started)
7. [API Documentation](#-api-documentation)

---

## 🚨 Problem Statement
**Targeting Problem Statement 1: AI-Powered Suspicious Activity Detection**

Financial institutions face strict mandates from regulatory bodies (FinCEN, FATF) to maintain robust AML compliance programs. However, traditional legacy systems suffer from two major flaws:
1. **Rule-Based Rigidity:** Simple thresholds generate a flood of false positives, exhausting compliance analysts.
2. **Evasion by Design:** Sophisticated laundering networks use *structuring*, *smurfing*, and *layering* to intentionally bypass traditional rules.

**The result:** A "Black Box" where compliance teams cannot explain why an AI flagged a transaction, leading to regulatory friction.

---

## 💡 Our Solution
FinShield AI solves this by deploying an **Autonomous Agentic Swarm**. 

Instead of a black-box model, FinShield acts as an AI Investigation Partner. It parses natural language queries using **Gemini 2.5 Flash**, dynamically coordinates 9 specialized AI Agents via **LangGraph**, and generates a fully transparent, evidence-backed Suspicious Activity Report (SAR). 

FinShield fuses deterministic rules (for regulatory compliance) with unsupervised machine learning (Isolation Forests) into a hybrid risk engine.

---

## 🤖 Agentic Swarm Architecture
FinShield AI abandons the concept of a "fixed pipeline". Instead, it utilizes an advanced **LangGraph Multi-Agent Topology**.

### The 9-Agent Swarm
When an investigation is triggered, the **Supervisor Agent** coordinates:
1. 👤 **Customer Agent**: Analyzes KYC profile, risk history, and jurisdiction.
2. 💸 **Transaction Agent**: Calculates velocity, rolling sums, and temporal cash flows.
3. 🕸️ **Network Agent**: Traces entity linkage and graph connectivity risk.
4. 📜 **Rule Intelligence Agent**: Executes deterministic AML regulations (e.g., structuring alerts, FATF lists).
5. 🧠 **ML Intelligence Agent**: Runs unsupervised anomaly detection (Isolation Forest) on engineered features.
6. ⚖️ **Compliance Agent**: Fuses ML scores and Rule triggers into a final Hybrid Risk Score.
7. 🧩 **Evidence Aggregator**: Compiles a structured evidence graph with attribution percentages.
8. 📝 **Report Generator**: Synthesizes the evidence via Gemini into a human-readable SAR.
9. 🗄️ **Audit Agent**: Logs all immutable actions to the SQLite database.

### Detection Techniques
- **Structuring / Smurfing:** Rule-004 detects split payments avoiding reporting thresholds.
- **High-Risk Jurisdiction:** Rule-012 flags transfers to FATF grey/black-list countries.
- **Rapid Cash-Out:** Rule-008 detects high-velocity cash withdrawals.
- **Unsupervised Anomalies:** Machine learning identifies unknown threat vectors.

---

## 📊 Dataset & Scale
We utilize the **IBM AML Simulation Dataset** (1.3M+ rows), which provides highly realistic, imbalanced fraud data containing fan-in, fan-out, and bipartite laundering topologies.

| File | Rows | Description |
|------|------|-------------|
| `transactions.csv` | **1,323,234** | The core financial transaction ledger. |
| `accounts.csv` | ~10,000 | Account and customer KYC metadata. |
| `alerts.csv` | 1,719+ | Known suspicious alert events (0.13% fraud rate). |

---

## 🛠 Tech Stack
| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Agentic AI** | LangGraph, LangChain, Google Gemini API (`gemini-2.5-flash`) |
| **Machine Learning** | scikit-learn (Isolation Forest), Pandas, NumPy |
| **Database** | SQLite (Immutable Audit Trails) |
| **DevOps** | Docker, Docker Compose |

---

## 🚀 Getting Started

The platform is fully containerized. You do not need to install Python or Node locally!

### Prerequisites
- [Docker & Docker Compose](https://www.docker.com/)
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com).

### 1. Clone & Configure
```bash
git clone https://github.com/subh-ghosh/finshield-ai.git
cd finshield-ai

# Configure your API key
cp backend/.env.example backend/.env
# Open backend/.env and paste your GEMINI_API_KEY
```

### 2. Boot the Platform
```bash
docker-compose up --build
```
*Note: On the first boot, the backend will process the 1.3M row dataset and build the ML models. This takes ~60 seconds. Subsequent boots use the cache instantly.*

### 3. Access
- **Investigation Dashboard (Frontend)**: [http://localhost:5173](http://localhost:5173)
- **OpenAPI Swagger (Backend)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 API Documentation
FinShield exposes a rich REST API for enterprise integration.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/planner/investigate` | POST | Triggers the 9-Agent LangGraph Swarm to investigate a customer. |
| `/api/v1/risk-classify/{id}` | GET | Returns the Hybrid Risk Score (Rules + ML) for an entity. |
| `/api/v1/simulation/what-if` | POST | Counterfactual simulator: predicts risk changes before transactions occur. |
| `/api/v1/anomaly/{id}` | GET | Isolation Forest anomaly scoring and confidence metrics. |
| `/api/v1/customer/{id}` | GET | Fetches the engineered feature vector and KYC profile. |

---

### External Tools Disclosure
*As required by Hackathon rules:*
- **Google Gemini API (`gemini-2.5-flash`)**: Powers agent intent parsing, reasoning, and report synthesis.
- **LangGraph & LangChain**: Open-source framework used for Multi-Agent Orchestration.
- **react-force-graph-2d**: Open-source visualization for the Knowledge Graph.
- **scikit-learn**: Open-source library used for the Isolation Forest ML model.
