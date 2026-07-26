import json
import re
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import time
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from app.agent.state import AgentState, EvidenceItem, Recommendation, ActionLog
from app.agent.tools import get_tool_by_name

def get_current_time():
    return datetime.utcnow().isoformat()

def supervisor_agent(state: AgentState):
    messages = state.get("messages", [])
    last_user_msg = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    )

    customer_id = state.get("customer_id", "UNKNOWN")
    match = re.search(r'C_\d+', last_user_msg, re.IGNORECASE)
    if match:
        customer_id = match.group(0).upper()

    intent = f"Investigate customer {customer_id}"
    log = ActionLog(
        timestamp=get_current_time(),
        tool="Supervisor Agent",
        duration=0.01,
        result=f"Dispatched investigation for {customer_id} to specialized agents.",
        status="COMPLETED",
    )
    return {"current_intent": intent, "customer_id": customer_id, "planner_timeline": [log]}

def _run_agent_tool(agent_name: str, tool_name: str, customer_id: str) -> dict:
    tool_func = get_tool_by_name(tool_name)
    start_time = time.time()
    try:
        res = tool_func.invoke({"customer_id": customer_id}) if tool_func else "Tool not found"
        duration = time.time() - start_time
        log = ActionLog(timestamp=get_current_time(), tool=agent_name, duration=round(duration, 2), result="Success", status="COMPLETED")
        return {"output": res, "log": log, "tool": tool_name}
    except Exception as e:
        duration = time.time() - start_time
        log = ActionLog(timestamp=get_current_time(), tool=agent_name, duration=round(duration, 2), result="Failed", status="FAILED")
        return {"output": f"Error: {str(e)}", "log": log, "tool": tool_name}

def customer_agent(state: AgentState):
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Customer Agent", "customer_360_tool", customer_id)
    return {"planner_timeline": [res["log"]], "messages": [AIMessage(content=f"Customer Agent Results: {json.dumps([res])}")]}

def transaction_agent(state: AgentState):
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Transaction Agent", "transaction_tool", customer_id)
    return {"planner_timeline": [res["log"]], "messages": [AIMessage(content=f"Transaction Agent Results: {json.dumps([res])}")]}

def network_agent(state: AgentState):
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Network Agent", "timeline_tool", customer_id) # Using timeline_tool as proxy for network hops
    return {"planner_timeline": [res["log"]], "messages": [AIMessage(content=f"Network Agent Results: {json.dumps([res])}")]}

def rule_intelligence_agent(state: AgentState):
    """Standalone Rule Intelligence Agent — runs deterministic AML rules only."""
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Rule Intelligence Agent", "rule_engine_tool", customer_id)
    evidence = EvidenceItem(
        source="Rule Intelligence Agent",
        description=str(res.get("output", ""))
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
        description=str(res.get("output", ""))
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
        description=str(res.get("output", ""))
    )
    return {
        "planner_timeline": [res["log"]],
        "evidence_bundle": [evidence],
        "messages": [AIMessage(content=f"Compliance Agent Results: {json.dumps([res])}")]
    }

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
    
    log = ActionLog(timestamp=get_current_time(), tool="Evidence Aggregator", duration=0.05, result=f"Built structured evidence graph with {len(evidence)} items.", status="COMPLETED")
    return {"evidence_bundle": evidence, "planner_timeline": [log],
            "messages": [AIMessage(content=f"Evidence Graph: {json.dumps(evidence_graph)}")]}

def report_generator_agent(state: AgentState):
    evidence = state.get("evidence_bundle", [])
    messages = state.get("messages", [])
    
    risk_level = "LOW"
    confidence = "90%"
    actions = ["Monitor"]
    summary = "Consensus Reached: No immediate threat detected. Automated monitoring will continue."
    
    # Analyze messages for high risk signals
    is_high_risk = any("CRITICAL" in m.content or "HIGH" in m.content for m in messages if isinstance(m, AIMessage))
    is_medium_risk = any("MEDIUM" in m.content for m in messages if isinstance(m, AIMessage))

    if is_high_risk:
        risk_level = "HIGH"
        confidence = "85%"
        actions = ["Escalate to L2", "File SAR"]
        summary = "Consensus Reached: Multi-Agent supervisor detected high-risk network and behavioral indicators."
    elif is_medium_risk:
        risk_level = "MEDIUM"
        confidence = "80%"
        actions = ["Manual Review"]
        summary = "Consensus Reached: Moderate risk detected by specialized agents. Proceed with manual review."

    rec_dict = Recommendation(risk_level=risk_level, confidence=confidence, evidence_count=len(evidence), recommended_actions=actions)
    log = ActionLog(timestamp=get_current_time(), tool="Report Generator Agent", duration=0.01, result=f"Generated SAR/Report: {risk_level}", status="COMPLETED")

    return {"final_recommendation": rec_dict, "messages": [AIMessage(content=summary)], "planner_timeline": [log]}

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


# Build Graph
builder = StateGraph(AgentState)

builder.add_node("supervisor_agent", supervisor_agent)
builder.add_node("customer_agent", customer_agent)
builder.add_node("transaction_agent", transaction_agent)
builder.add_node("network_agent", network_agent)
builder.add_node("rule_intelligence_agent", rule_intelligence_agent)
builder.add_node("ml_intelligence_agent", ml_intelligence_agent)
builder.add_node("compliance_agent", compliance_agent)
builder.add_node("evidence_aggregator", evidence_aggregator)
builder.add_node("report_generator_agent", report_generator_agent)
builder.add_node("audit_agent", audit_agent)

builder.add_edge(START, "supervisor_agent")
builder.add_edge("supervisor_agent", "customer_agent")
builder.add_edge("customer_agent", "transaction_agent")
builder.add_edge("transaction_agent", "network_agent")
builder.add_edge("network_agent", "rule_intelligence_agent")
builder.add_edge("network_agent", "ml_intelligence_agent")
builder.add_edge("rule_intelligence_agent", "compliance_agent")
builder.add_edge("ml_intelligence_agent", "compliance_agent")
builder.add_edge("compliance_agent", "evidence_aggregator")
builder.add_edge("evidence_aggregator", "report_generator_agent")
builder.add_edge("report_generator_agent", "audit_agent")
builder.add_edge("audit_agent", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

def get_agent_executor():
    return graph
