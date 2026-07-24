# FinShield AI
An Agentic AI-powered Anti-Money Laundering (AML) Investigation Platform built for the Campus Hackathon 2026.

## Problem Statement
AI-Powered Suspicious Activity Detection (Problem Statement 1). 
FinShield AI is a planner-driven, tool-using autonomous agent that performs intelligent AML investigations, dynamically selects analytical tools, and provides explainable, evidence-backed risk assessments.

## Why FinShield AI?
Traditional AML systems throw "black box" alerts at analysts, leading to massive false positive rates and hours of manual data collection across fragmented systems. 
FinShield AI solves this by acting as an **AI Investigation Partner**:
1. **Dynamic Execution**: It doesn't run a static pipeline. It parses the user query, determines intent, and dynamically orchestrates the right tools (e.g., skips dataset-wide anomaly detection if the user just asks to investigate a single customer).
2. **Explainability**: "Risk is High" is not enough. FinShield AI provides concrete evidence: "15 transfers below reporting threshold, velocity 9x normal."
3. **Enterprise Workflow**: It features a unified Customer360 view, an Evidence Panel, a live Execution Graph, and automated Report Generation.

## Tech Stack
*   **Frontend**: React, Tailwind CSS, shadcn/ui
*   **Backend**: FastAPI (Python)
*   **AI Agent**: LangGraph, Gemini 3.1 Pro API
*   **Machine Learning**: scikit-learn (Isolation Forest), custom rule engine
*   **Database**: PostgreSQL / SQLite (for rapid prototyping)

## Project Structure
```
FinShield/
├── backend/          # FastAPI server, LangGraph Agent, ML models
├── frontend/         # React UI
├── docs/             # High-level architecture and design documents
└── data/             # Datasets for analysis
```

## Documentation
The architectural vision and system design are detailed in the `docs/` folder:
- [Project Bible](docs/01_project_bible.md)
- [Architecture & Design](docs/02_architecture.md)
- [API Specifications](docs/03_api_specification.md)
- [Database Schema](docs/04_database_schema.md)
- [Requirements & Use Cases](docs/05_requirements.md)

## Setup Instructions
*(To be completed during the hackathon)*

## Data Sources
*(To be completed - listing Kaggle/public datasets used)*
