# FinShield Nexus V2 — Full Implementation Guide & Task Division

> **Share this document with Arhit.** It contains everything both of you need to work independently.

---

## 👥 Team & Workflow Rules

| Person | Machine | AI Assistant | Branch |
|--------|---------|-------------|--------|
| **Subarta** | Laptop 1 | Antigravity Instance 1 | `master` (or `subarta-v2`) |
| **Arhit** | Laptop 2 | Antigravity Instance 2 | `arhit-v2` |

### Golden Rules
1. **NEVER edit each other's files.** Every file is owned by exactly one person.
2. Work on separate Git branches. Merge at the end via PR.
3. If you need data from the other person's module, define a **contract** (API endpoint or TypeScript interface) upfront. Build against the contract, not the implementation.
4. When done, Subarta merges Arhit's branch into master. One integration session at the end.

---

## 📂 Current Codebase Map (For Reference)

```
backend/
├── app/
│   ├── agent/          ← LangGraph multi-agent system
│   │   ├── graph.py       (Subarta owns)
│   │   ├── state.py       (Subarta owns)
│   │   └── tools.py       (Subarta owns)
│   ├── api/
│   │   ├── endpoints/     (Legacy — don't touch)
│   │   └── v1/routers/
│   │       ├── analysis.py
│   │       ├── customer.py
│   │       ├── graph.py      (Arhit owns)
│   │       ├── health.py
│   │       ├── memory.py
│   │       ├── metrics.py
│   │       ├── planner.py
│   │       ├── queue.py
│   │       ├── router.py     (SHARED — only add import lines)
│   │       └── similar_cases.py
│   ├── explainability/     (Subarta owns)
│   ├── ml/                 (Arhit owns)
│   ├── rules/              (Arhit owns)
│   ├── services/
│   │   ├── graph_analysis.py  (Arhit owns)
│   │   ├── pipeline.py       (Shared — careful)
│   │   └── ...others
│   └── db/                 (Arhit owns)
frontend/
├── src/
│   ├── pages/
│   │   ├── InvestigationWorkspace.tsx  (Subarta owns)
│   │   ├── Dashboard.tsx              (Subarta owns)
│   │   └── PlannerPlayground.tsx      (Subarta owns)
│   └── components/investigation/
│       ├── AgentSwarmView.tsx            (Subarta owns)
│       ├── EvidenceConsensusBoard.tsx    (Subarta owns)
│       ├── KnowledgeGraph.tsx           (Arhit owns)
│       └── ... (new components below)
```

---

# 🔵 SUBARTA'S TRACKS (Track S)

Everything below is **Subarta's** work. Arhit must NOT touch these files.

---

## S1. Split Agents: Rule Agent & ML Agent (Phase 2 Completion)

### Why
Right now, `compliance_agent` in `graph.py` calls rule_engine, isolation_forest, AND hybrid_risk all in one function. The V2 vision requires **9 distinct agents**, each with their own memory, reasoning, and specialization. We currently have 7 — we're missing a standalone Rule Agent and ML Agent (currently merged into Compliance).

### What
Split the `compliance_agent()` function into 3 separate agents:
- `rule_intelligence_agent()` — Only runs rule_engine_tool
- `ml_intelligence_agent()` — Only runs isolation_forest_tool
- `compliance_agent()` — Only runs hybrid_risk_tool (fuses rule + ML)

### How — Exact Implementation

**File:** `backend/app/agent/graph.py` (Subarta owns)

```python
# Replace the single compliance_agent with 3 agents:

def rule_intelligence_agent(state: AgentState):
    """Standalone Rule Intelligence Agent — runs deterministic AML rules only."""
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Rule Intelligence Agent", "rule_engine_tool", customer_id)
    evidence = EvidenceItem(
        source="Rule Intelligence Agent",
        description=res["output"]
    )
    return {
        "planner_timeline": [res["log"]],
        "evidence_bundle": [evidence],
        "messages": [AIMessage(content=f"Rule Intelligence Agent Results: {json.dumps([res])}")]
    }

def ml_intelligence_agent(state: AgentState):
    """Standalone ML Intelligence Agent — runs Isolation Forest only."""
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("ML Intelligence Agent", "isolation_forest_tool", customer_id)
    evidence = EvidenceItem(
        source="ML Intelligence Agent",
        description=res["output"]
    )
    return {
        "planner_timeline": [res["log"]],
        "evidence_bundle": [evidence],
        "messages": [AIMessage(content=f"ML Intelligence Agent Results: {json.dumps([res])}")]
    }

def compliance_agent(state: AgentState):
    """Compliance Agent — fuses rule + ML into hybrid risk assessment."""
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Compliance Agent", "hybrid_risk_tool", customer_id)
    evidence = EvidenceItem(
        source="Compliance Agent",
        description=res["output"]
    )
    return {
        "planner_timeline": [res["log"]],
        "evidence_bundle": [evidence],
        "messages": [AIMessage(content=f"Compliance Agent Results: {json.dumps([res])}")]
    }
```

Update the graph wiring:
```python
builder.add_node("rule_intelligence_agent", rule_intelligence_agent)
builder.add_node("ml_intelligence_agent", ml_intelligence_agent)
# Run rule + ML in parallel, then compliance fuses them
builder.add_edge("network_agent", "rule_intelligence_agent")
builder.add_edge("network_agent", "ml_intelligence_agent")
builder.add_edge("rule_intelligence_agent", "compliance_agent")
builder.add_edge("ml_intelligence_agent", "compliance_agent")
```

### Files Touched
- `backend/app/agent/graph.py` — Refactor agents, update wiring

---

## S2. Add Audit Agent (Phase 2)

### Why
Regulatory compliance (FATF, MAS, ACAMS) requires a full audit trail of every AI decision. Currently no agent logs decisions for auditors.

### What
A new `audit_agent` node that runs at the very end of the graph, after the report generator. It collects the entire `planner_timeline` and `evidence_bundle`, serializes them into an audit log, and stores it.

### How

**File:** `backend/app/agent/graph.py`

```python
def audit_agent(state: AgentState):
    """Audit Agent — creates immutable audit trail for regulatory compliance."""
    timeline = state.get("planner_timeline", [])
    evidence = state.get("evidence_bundle", [])
    recommendation = state.get("final_recommendation", {})
    customer_id = state.get("customer_id", "UNKNOWN")
    
    audit_record = {
        "customer_id": customer_id,
        "timestamp": get_current_time(),
        "agent_actions": [
            {"agent": t["tool"], "status": t["status"], "duration": t["duration"]}
            for t in timeline
        ],
        "evidence_count": len(evidence),
        "final_risk": recommendation.get("risk_level", "UNKNOWN"),
        "confidence": recommendation.get("confidence", "UNKNOWN"),
    }
    
    # Store to investigation memory (append-only log)
    log = ActionLog(
        timestamp=get_current_time(),
        tool="Audit Agent",
        duration=0.01,
        result=f"Audit trail created for {customer_id}: {len(timeline)} actions logged.",
        status="COMPLETED"
    )
    return {"planner_timeline": [log], "messages": [AIMessage(content=f"Audit Record: {json.dumps(audit_record)}")]}
```

Wire it after report_generator:
```python
builder.add_node("audit_agent", audit_agent)
builder.add_edge("report_generator_agent", "audit_agent")
builder.add_edge("audit_agent", END)  # Replace the old report_generator→END edge
```

### Files Touched
- `backend/app/agent/graph.py`

---

## S3. Add Monitoring Agent (Phase 2 + Phase 14)

### Why
Currently investigations are "fire and forget." The V2 vision says cases should **never truly die** — they should continuously monitor for new evidence.

### What
A new `monitoring_agent` that runs as a background check. After a case is investigated, it stores the customer_id in a watch list. When the pipeline re-runs (new data arrives), it automatically checks if any watched customers have new suspicious activity.

### How

**File:** `backend/app/agent/monitoring.py` (**NEW FILE** — Subarta owns)

```python
"""Monitoring Agent — Continuous case lifecycle management."""
import json
from datetime import datetime
from typing import Dict, List, Set

class MonitoringAgent:
    """Tracks investigated customers and flags re-emerging risk."""
    
    def __init__(self):
        self._watchlist: Dict[str, dict] = {}  # customer_id → {risk_level, last_checked, ...}
    
    def add_to_watchlist(self, customer_id: str, risk_level: str, evidence_count: int):
        self._watchlist[customer_id] = {
            "risk_level": risk_level,
            "evidence_count": evidence_count,
            "added_at": datetime.utcnow().isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "status": "MONITORING",
            "reopen_count": 0
        }
    
    def check_customer(self, customer_id: str, current_risk: float) -> dict:
        """Check if a monitored customer's risk has changed."""
        if customer_id not in self._watchlist:
            return {"action": "NONE"}
        
        entry = self._watchlist[customer_id]
        entry["last_checked"] = datetime.utcnow().isoformat()
        
        if current_risk > 75 and entry["risk_level"] in ["LOW", "MEDIUM"]:
            entry["status"] = "ESCALATED"
            entry["reopen_count"] += 1
            return {"action": "REOPEN", "reason": f"Risk escalated from {entry['risk_level']} to HIGH"}
        
        return {"action": "CONTINUE_MONITORING"}
    
    def get_watchlist(self) -> List[dict]:
        return [{"customer_id": k, **v} for k, v in self._watchlist.items()]
```

**File:** `backend/app/api/v1/routers/monitoring.py` (**NEW FILE** — Subarta owns)

Expose endpoints:
- `GET /api/v1/monitoring/watchlist` — Returns all monitored customers
- `POST /api/v1/monitoring/check/{customer_id}` — Triggers a re-check

### Files Touched
- `backend/app/agent/monitoring.py` (NEW)
- `backend/app/api/v1/routers/monitoring.py` (NEW)
- `backend/app/api/v1/routers/router.py` (add 1 import line only)

---

## S4. Agent Memory & State Tracking (Phase 2 + Phase 9)

### Why
Each agent currently is stateless — it runs, returns output, and forgets. The V2 vision requires every agent to have **persistent memory** so it can say "I investigated this customer 3 weeks ago and found X."

### What
Update `AgentState` in `state.py` to track:
- Which agent contributed each piece of evidence (already partially done)
- Per-agent memory slots
- Investigation history reference

### How

**File:** `backend/app/agent/state.py` (Subarta owns)

```python
class AgentMemoryEntry(TypedDict):
    agent_name: str
    customer_id: str
    timestamp: str
    findings_summary: str
    risk_contribution: float  # 0.0 - 1.0

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    customer_id: str
    current_intent: str
    execution_plan: List[str]
    execution_monitor: Annotated[Dict[str, str], merge_dict]
    evidence_bundle: Annotated[List[EvidenceItem], merge_list]
    final_recommendation: Recommendation
    planner_timeline: Annotated[List[ActionLog], merge_list]
    
    # NEW: Per-agent memory
    agent_memories: Annotated[List[AgentMemoryEntry], merge_list]
    # NEW: Investigation lifecycle
    case_status: str  # OPEN, MONITORING, ESCALATED, CLOSED
    investigation_id: str
```

### Files Touched
- `backend/app/agent/state.py`

---

## S5. Evidence Graph Engine (Phase 8)

### Why
Currently the system returns `Risk = 94` as a flat number. The V2 vision requires a structured **Evidence Graph** where each evidence type chains together: `Rule Evidence → ML Evidence → Graph Evidence → Timeline → Risk`.

### What
Refactor the `evidence_aggregator` to build a structured evidence chain, not just a flat list.

### How

**File:** `backend/app/agent/graph.py` — Refactor `evidence_aggregator()`

```python
def evidence_aggregator(state: AgentState):
    """Evidence Aggregator — builds a structured evidence graph."""
    evidence = state.get("evidence_bundle", [])
    
    # Categorize evidence by source type
    rule_evidence = [e for e in evidence if "Rule" in e["source"]]
    ml_evidence = [e for e in evidence if "ML" in e["source"]]
    graph_evidence = [e for e in evidence if "Network" in e["source"]]
    compliance_evidence = [e for e in evidence if "Compliance" in e["source"]]
    
    # Calculate risk attribution percentages
    total = len(evidence) or 1
    attribution = {
        "rule_pct": round(len(rule_evidence) / total * 100),
        "ml_pct": round(len(ml_evidence) / total * 100),
        "graph_pct": round(len(graph_evidence) / total * 100),
        "compliance_pct": round(len(compliance_evidence) / total * 100),
    }
    
    evidence_graph = {
        "layers": [
            {"name": "Rule Evidence", "count": len(rule_evidence), "items": rule_evidence},
            {"name": "ML Evidence", "count": len(ml_evidence), "items": ml_evidence},
            {"name": "Graph Evidence", "count": len(graph_evidence), "items": graph_evidence},
            {"name": "Compliance Evidence", "count": len(compliance_evidence), "items": compliance_evidence},
        ],
        "attribution": attribution
    }
    
    log = ActionLog(...)
    return {"evidence_bundle": evidence, "planner_timeline": [log],
            "messages": [AIMessage(content=f"Evidence Graph: {json.dumps(evidence_graph)}")]}
```

### Files Touched
- `backend/app/agent/graph.py`

---

## S6. Swarm View UI Enhancement (Phase 2 Frontend)

### Why
The current `AgentSwarmView.tsx` simulates parallel agent execution with static mock data. It needs to show the actual real-time agent execution trace from the backend's `planner_timeline`.

### What
Parse the `planner_timeline` from the API response and animate each agent's status as it completes.

### How

**File:** `frontend/src/components/investigation/AgentSwarmView.tsx` (Subarta owns)

- Parse `planner_timeline` array from investigation result
- Map each `ActionLog.tool` to an agent badge
- Show real `duration` values
- Add status transitions: WAITING → RUNNING → COMPLETED/FAILED
- Add the risk attribution percentages from the evidence graph

### Files Touched
- `frontend/src/components/investigation/AgentSwarmView.tsx`

---

## S7. Evidence Consensus Board Enhancement (Phase 8 + Phase 11 Frontend)

### Why
The `EvidenceConsensusBoard.tsx` currently shows mock data. It needs to render the real evidence graph structure with attribution percentages.

### What
Consume the evidence graph JSON from the investigation result and render:
- Grouped evidence items by agent
- Risk attribution progress bars (45% Rule, 35% ML, 20% Network)
- Consensus agreement/disagreement indicators

### How

**File:** `frontend/src/components/investigation/EvidenceConsensusBoard.tsx` (Subarta owns)

### Files Touched
- `frontend/src/components/investigation/EvidenceConsensusBoard.tsx`

---

## S8. Autonomous Case Lifecycle UI (Phase 14 Frontend)

### Why
Cases currently exist as one-shot investigations. The V2 vision requires a lifecycle: Open → Monitor → Update → Escalate → Reopen → Close → Monitor Again.

### What
Build a new `CaseLifecycleTimeline.tsx` component that shows the case status and transitions.

### How

**File:** `frontend/src/components/investigation/CaseLifecycleTimeline.tsx` (**NEW** — Subarta owns)

- Show a horizontal timeline of case state transitions
- Color-coded states: 🟢 Open, 🔵 Monitoring, 🟡 Update, 🔴 Escalated, ⚪ Closed
- Connect to `GET /api/v1/monitoring/watchlist` endpoint
- Allow analyst to manually transition states

### Files Touched
- `frontend/src/components/investigation/CaseLifecycleTimeline.tsx` (NEW)
- `frontend/src/pages/InvestigationWorkspace.tsx` (add import + render)

---

## S9. Explainability Engine Enhancement (Phase 8)

### Why
Regulatory compliance requires the AI to explain **exactly** why it flagged a customer. The current explainability module exists but doesn't integrate with the new multi-agent evidence graph.

### What
Update the explainability pipeline to consume the structured evidence graph from the multi-agent system.

### How

**File:** `backend/app/explainability/evidence_extractor.py` (Subarta owns)

- Accept the new `evidence_bundle` with per-agent attribution
- Generate natural language explanations for each evidence layer
- Output: "45% of the risk came from Rule Intelligence Agent detecting structuring patterns..."

### Files Touched
- `backend/app/explainability/evidence_extractor.py`
- `backend/app/explainability/explainability_service.py`

---

# 🟢 ARHIT'S TRACKS (Track A)

Everything below is **Arhit's** work. Subarta must NOT touch these files.

---

## A1. Expand Knowledge Graph Entity Types (Phase 3)

### Why
Currently the Knowledge Graph only has `customer` and basic transaction edges. The V2 vision requires **11 entity types**: Customer, Account, Company, Director/UBO, Phone, Email, IP, Wallet, Merchant, Country, Transaction.

### What
Expand `GraphAnalyzer.get_ego_graph()` to detect and categorize more entity types from the dataset columns.

### How

**File:** `backend/app/services/graph_analysis.py` (Arhit owns)

The current `get_ego_graph` method only uses sender/receiver columns. Expand it to:
1. Scan for IP columns (e.g., `ip_address`, `login_ip`)
2. Scan for device columns (e.g., `device_id`)
3. Scan for country/jurisdiction columns
4. Assign node `group` based on detected column type
5. Add edges like "logged_in_from", "registered_device", "jurisdiction"

```python
# Entity type detection heuristic
ENTITY_COLUMN_MAP = {
    "ip": ["ip_address", "login_ip", "source_ip"],
    "device": ["device_id", "device_fingerprint"],
    "country": ["country", "jurisdiction", "country_code"],
    "merchant": ["merchant_id", "merchant_name"],
    "email": ["email", "email_address"],
    "phone": ["phone", "phone_number", "mobile"],
    "wallet": ["wallet_id", "crypto_wallet"],
}
```

### Files Touched
- `backend/app/services/graph_analysis.py`

---

## A2. Graph API Enhancement (Phase 3)

### Why
The current `/api/v1/graph/{customer_id}` only returns a basic ego graph. Enhance it with filtering, expanded metadata, and risk overlays.

### What
Add query parameters and richer response:
- `GET /api/v1/graph/{customer_id}?hops=3&entity_types=customer,company,ip`
- Response should include `risk_score` per node and `transaction_volume` per edge

### How

**File:** `backend/app/api/v1/routers/graph.py` (Arhit owns)

```python
@router.get("/graph/{customer_id}")
def get_graph(
    customer_id: str,
    hops: int = 2,
    entity_types: str = None,  # comma-separated filter
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
):
    graph_data = analyzer.get_ego_graph(
        customer_id,
        pipeline_res.clean_dataframe,
        max_hops=hops
    )
    
    # Filter by entity types if specified
    if entity_types:
        allowed = set(entity_types.split(","))
        graph_data["nodes"] = [n for n in graph_data["nodes"] if n["group"] in allowed]
        # Filter edges to only include filtered nodes
        node_ids = {n["id"] for n in graph_data["nodes"]}
        graph_data["links"] = [e for e in graph_data["links"] if e["source"] in node_ids and e["target"] in node_ids]
    
    return graph_data
```

### Files Touched
- `backend/app/api/v1/routers/graph.py`

---

## A3. Graph Neural Network (Phase 4)

### Why
Isolation Forest treats each customer independently. GNNs learn from the **relational structure** — a customer connected to 3 shell companies is riskier than one connected to 3 retail stores. This is the #1 research direction in AML.

### What
Implement a simple Graph Convolutional Network (GCN) that takes the transaction graph as input and outputs a per-node risk score. This score is then ensembled with the existing Isolation Forest score.

### How

**File:** `backend/app/ml/gnn_model.py` (**NEW** — Arhit owns)

```python
"""Graph Neural Network for relational risk scoring."""
import numpy as np
from typing import Dict, List, Tuple

class SimpleGCN:
    """Lightweight GCN that runs without PyTorch/TensorFlow.
    Uses numpy-only message passing for hackathon portability.
    """
    
    def __init__(self, n_layers: int = 2, hidden_dim: int = 16):
        self.n_layers = n_layers
        self.hidden_dim = hidden_dim
        self.weights = []  # Initialized during fit
    
    def _build_adjacency(self, edges: List[Tuple[str, str]], node_index: Dict[str, int]) -> np.ndarray:
        """Build normalized adjacency matrix from edge list."""
        n = len(node_index)
        A = np.zeros((n, n))
        for src, dst in edges:
            if src in node_index and dst in node_index:
                A[node_index[src], node_index[dst]] = 1.0
                A[node_index[dst], node_index[src]] = 1.0  # undirected
        
        # Add self-loops and normalize
        A += np.eye(n)
        D = np.diag(1.0 / np.sqrt(A.sum(axis=1) + 1e-8))
        return D @ A @ D
    
    def fit_predict(self, nodes: List[str], edges: List[Tuple[str, str]], 
                    node_features: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Run GCN message passing and return per-node risk scores."""
        node_index = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        
        # Build feature matrix
        feat_dim = len(next(iter(node_features.values()))) if node_features else 4
        X = np.zeros((n, feat_dim))
        for node, idx in node_index.items():
            if node in node_features:
                X[idx] = node_features[node]
        
        # Adjacency
        A_norm = self._build_adjacency(edges, node_index)
        
        # Initialize weights (Xavier-like)
        np.random.seed(42)
        dims = [feat_dim] + [self.hidden_dim] * self.n_layers + [1]
        self.weights = [np.random.randn(dims[i], dims[i+1]) * 0.5 for i in range(len(dims)-1)]
        
        # Forward pass (message passing)
        H = X
        for W in self.weights[:-1]:
            H = A_norm @ H @ W
            H = np.maximum(H, 0)  # ReLU
        
        # Final layer → risk score
        H = A_norm @ H @ self.weights[-1]
        scores = 1 / (1 + np.exp(-H))  # Sigmoid to [0,1]
        
        return {node: float(scores[idx][0]) * 100 for node, idx in node_index.items()}
```

### Integration
The GCN output is combined in the hybrid risk engine:
```
final_risk = 0.3 * rule_score + 0.3 * isolation_forest_score + 0.4 * gnn_score
```

**File:** `backend/app/ml/hybrid_risk_engine.py` (Arhit owns) — Add GNN score fusion

### Files Touched
- `backend/app/ml/gnn_model.py` (NEW)
- `backend/app/ml/hybrid_risk_engine.py` (modify score fusion)

---

## A4. Temporal GNN (Phase 4 Extension)

### Why
A basic GCN is static — it doesn't know whether transactions happened yesterday or 6 months ago. Temporal GNNs detect patterns that **evolve over time**, like a sudden burst of connections to a dormant shell company.

### What
Extend the GCN with time-windowed snapshots. Build separate adjacency matrices for different time periods and combine them.

### How

**File:** `backend/app/ml/gnn_model.py` (Arhit owns)

Add a `TemporalGCN` class that:
1. Splits transactions into time windows (e.g., 7-day buckets)
2. Builds a GCN snapshot for each window
3. Aggregates node scores across windows (exponential decay — recent windows weighted more)

### Files Touched
- `backend/app/ml/gnn_model.py`

---

## A5. Self-Building Rule Engine (Phase 19)

### Why
Currently, all rules are hardcoded Python classes. The V2 vision says the AI should **suggest new rules** based on patterns it discovers, which humans review and approve.

### What
Build a `RuleSuggestionEngine` that analyzes the feature distribution and proposes new threshold rules.

### How

**File:** `backend/app/rules/rule_suggestion_engine.py` (**NEW** — Arhit owns)

```python
"""AI-driven rule suggestion engine — proposes new deterministic rules."""
import pandas as pd
import numpy as np
from typing import List, Dict

class RuleSuggestion:
    def __init__(self, name: str, description: str, column: str, 
                 operator: str, threshold: float, confidence: float):
        self.name = name
        self.description = description
        self.column = column
        self.operator = operator
        self.threshold = threshold
        self.confidence = confidence

class RuleSuggestionEngine:
    """Analyzes feature distributions to suggest new AML rules."""
    
    def suggest_rules(self, features_df: pd.DataFrame, 
                      anomaly_scores: Dict[str, float]) -> List[RuleSuggestion]:
        suggestions = []
        
        # Find columns where high-anomaly customers cluster at extreme values
        high_risk_ids = [cid for cid, score in anomaly_scores.items() if score > 80]
        
        for col in features_df.select_dtypes(include=[np.number]).columns:
            if col == 'customer_id':
                continue
            
            high_risk_vals = features_df[features_df['customer_id'].isin(high_risk_ids)][col]
            normal_vals = features_df[~features_df['customer_id'].isin(high_risk_ids)][col]
            
            if len(high_risk_vals) < 3:
                continue
            
            # If high-risk customers are all above the 95th percentile of normals
            p95 = normal_vals.quantile(0.95) if len(normal_vals) > 0 else 0
            pct_above = (high_risk_vals > p95).mean()
            
            if pct_above > 0.7:  # 70%+ of high-risk customers exceed this threshold
                suggestions.append(RuleSuggestion(
                    name=f"Auto_{col}_Threshold",
                    description=f"Flag customers where {col} > {p95:.2f} (95th percentile). {pct_above*100:.0f}% of high-risk customers exceed this.",
                    column=col,
                    operator=">",
                    threshold=float(p95),
                    confidence=float(pct_above)
                ))
        
        return sorted(suggestions, key=lambda s: s.confidence, reverse=True)[:10]
```

**File:** `backend/app/api/v1/routers/rules.py` (**NEW** — Arhit owns)

Expose endpoint:
- `GET /api/v1/rules/suggestions` — Returns AI-suggested rules for human review
- `POST /api/v1/rules/approve/{rule_name}` — Human approves a suggested rule

### Files Touched
- `backend/app/rules/rule_suggestion_engine.py` (NEW)
- `backend/app/api/v1/routers/rules.py` (NEW)
- `backend/app/api/v1/routers/router.py` (add 1 import line)

---

## A6. Knowledge Graph UI Enhancement (Phase 3 Frontend)

### Why
The current `KnowledgeGraph.tsx` renders a basic 2D force graph. It needs entity-type filtering, risk coloring, and click-to-expand functionality.

### What
Add a filter panel, color nodes by risk level (green/yellow/red), and implement "click node to expand 1 more hop."

### How

**File:** `frontend/src/components/investigation/KnowledgeGraph.tsx` (Arhit owns)

- Add filter checkboxes for entity types (Customer, Company, IP, etc.)
- Color nodes by risk: green (<30), yellow (30-70), red (>70)
- On node click, fetch `GET /api/v1/graph/{clicked_node_id}?hops=1` and merge new nodes into existing graph
- Add edge labels showing transaction amounts

### Files Touched
- `frontend/src/components/investigation/KnowledgeGraph.tsx`

---

## A7. Rule Suggestions UI (Phase 19 Frontend)

### Why
The backend suggests rules, but analysts need a UI to review and approve/reject them.

### What
Build a new page or widget that shows AI-suggested rules with approve/reject buttons.

### How

**File:** `frontend/src/components/investigation/RuleSuggestionsWidget.tsx` (**NEW** — Arhit owns)

- Fetch from `GET /api/v1/rules/suggestions`
- Show each suggestion as a card with: rule name, description, confidence %, column, threshold
- "Approve" button → `POST /api/v1/rules/approve/{name}`
- "Reject" button → dismisses locally

### Files Touched
- `frontend/src/components/investigation/RuleSuggestionsWidget.tsx` (NEW)

---

## A8. Simulation Engine Backend (Phase 6)

### Why
Analysts need to ask "What if this customer moves ₹5 crore tomorrow?" and get predictions **before** it happens. A `counterfactual_simulator.py` already exists but needs to be wired to the new multi-agent pipeline.

### What
Extend the existing counterfactual simulator to:
1. Accept a hypothetical transaction
2. Run it through the rule engine, ML model, and graph model
3. Return predicted triggers without actually modifying data

### How

**File:** `backend/app/services/counterfactual_simulator.py` (Arhit owns — already exists)

- Add a `simulate_transaction()` method
- Inject hypothetical transaction into a copy of the dataframe
- Run through the rule engine, isolation forest, and GNN
- Return: which rules would trigger, ML anomaly delta, graph risk delta

**File:** `backend/app/api/v1/routers/simulation.py` (**NEW** — Arhit owns)

Expose endpoint:
- `POST /api/v1/simulation/what-if` 
- Body: `{"customer_id": "C_123", "amount": 5000000, "recipient": "SHELL_CORP_X"}`
- Returns: predicted rule triggers, ML score change, graph risk change

### Files Touched
- `backend/app/services/counterfactual_simulator.py`
- `backend/app/api/v1/routers/simulation.py` (NEW)
- `backend/app/api/v1/routers/router.py` (add 1 import line)

---

# 🔗 SHARED CONTRACTS (API Interfaces)

These are the **contracts** both of you agree on upfront. Build your code against these interfaces so integration is seamless.

## Contract 1: Evidence Bundle Format

Both Subarta's agent system and Arhit's UI components must agree on this shape:

```typescript
// TypeScript interface for frontend
interface EvidenceBundle {
  layers: {
    name: string;        // "Rule Evidence", "ML Evidence", "Graph Evidence"
    count: number;
    items: { source: string; description: string }[];
  }[];
  attribution: {
    rule_pct: number;     // e.g., 45
    ml_pct: number;       // e.g., 35
    graph_pct: number;    // e.g., 15
    compliance_pct: number; // e.g., 5
  };
}
```

## Contract 2: Agent Timeline Format

```typescript
interface AgentTimelineEntry {
  timestamp: string;
  tool: string;       // Agent name
  duration: number;   // seconds
  result: string;
  status: "WAITING" | "RUNNING" | "COMPLETED" | "FAILED";
}
```

## Contract 3: Graph API Response

```typescript
interface GraphResponse {
  nodes: {
    id: string;
    name: string;
    group: "customer" | "company" | "ip" | "device" | "country" | "merchant" | "wallet" | "phone" | "email";
    val: number;           // node size
    risk_score?: number;   // 0-100
  }[];
  links: {
    source: string;
    target: string;
    name: string;          // edge label
    weight?: number;       // transaction amount
  }[];
}
```

## Contract 4: Rule Suggestion Response

```typescript
interface RuleSuggestion {
  name: string;
  description: string;
  column: string;
  operator: string;
  threshold: number;
  confidence: number;   // 0.0 - 1.0
}
```

---

# 🔀 INTEGRATION PLAN (Final Merge)

Once both tracks are complete, the merge is simple:

### Step 1: Arhit pushes his branch `arhit-v2`
### Step 2: Subarta pulls and merges
```bash
git fetch origin
git merge origin/arhit-v2
```

### Step 3: Only file that BOTH touched
`backend/app/api/v1/routers/router.py` — Resolve by keeping BOTH import lines:
```python
from app.api.v1.routers.monitoring import router as monitoring_router
from app.api.v1.routers.rules import router as rules_router
from app.api.v1.routers.simulation import router as simulation_router

v1_router.include_router(monitoring_router)
v1_router.include_router(rules_router)
v1_router.include_router(simulation_router)
```

### Step 4: Wire Arhit's components into Subarta's pages
Subarta drops Arhit's new components into `InvestigationWorkspace.tsx`:
```tsx
import { RuleSuggestionsWidget } from '../components/investigation/RuleSuggestionsWidget';
// Add to the workspace layout
```

### Step 5: Test everything end-to-end
```bash
cd backend && venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

---

# 📊 COMPLETE TASK SUMMARY

## Subarta's Tasks (9 items)
| ID | Task | New Files | Modified Files |
|----|------|-----------|----------------|
| S1 | Split Rule Agent & ML Agent | — | `agent/graph.py` |
| S2 | Add Audit Agent | — | `agent/graph.py` |
| S3 | Add Monitoring Agent | `agent/monitoring.py`, `routers/monitoring.py` | `routers/router.py` |
| S4 | Agent Memory & State Tracking | — | `agent/state.py` |
| S5 | Evidence Graph Engine | — | `agent/graph.py` |
| S6 | Swarm View UI Enhancement | — | `AgentSwarmView.tsx` |
| S7 | Evidence Consensus Board Enhancement | — | `EvidenceConsensusBoard.tsx` |
| S8 | Case Lifecycle Timeline UI | `CaseLifecycleTimeline.tsx` | `InvestigationWorkspace.tsx` |
| S9 | Explainability Engine Enhancement | — | `explainability/*.py` |

## Arhit's Tasks (8 items)
| ID | Task | New Files | Modified Files |
|----|------|-----------|----------------|
| A1 | Expand Knowledge Graph Entities | — | `services/graph_analysis.py` |
| A2 | Graph API Enhancement | — | `routers/graph.py` |
| A3 | Graph Neural Network | `ml/gnn_model.py` | `ml/hybrid_risk_engine.py` |
| A4 | Temporal GNN | — | `ml/gnn_model.py` |
| A5 | Self-Building Rule Engine | `rules/rule_suggestion_engine.py`, `routers/rules.py` | `routers/router.py` |
| A6 | Knowledge Graph UI Enhancement | — | `KnowledgeGraph.tsx` |
| A7 | Rule Suggestions UI | `RuleSuggestionsWidget.tsx` | — |
| A8 | Simulation Engine Backend | `routers/simulation.py` | `counterfactual_simulator.py` |

## Zero File Conflicts ✅
No file appears in both Subarta's and Arhit's columns (except `router.py` which only needs import lines added).

---

> *"Don't aim to build the best hackathon project. Aim to build the Bloomberg Terminal + Palantir Foundry + Microsoft Security Copilot for Financial Crime."*
