import json
import re
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import time
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from app.agent.state import AgentState, EvidenceItem, Recommendation, ActionLog
from app.agent.tools import get_tool_by_name

# Import SQLite DB session and models
from app.db.session import SessionLocal, init_db
from app.db.models import AuditLog as DBAuditLog

# Ensure DB tables are created
init_db()

def get_current_time():
    return datetime.utcnow().isoformat()

# Pydantic schemas for structured LLM outputs
class SupervisorIntent(BaseModel):
    intent: str = Field(description="The detected intent. Must be 'structuring', 'threshold', or 'single_entity'.")
    customer_id: str = Field(description="The customer ID extracted from the prompt, e.g. 'C_123'. Defaults to 'UNKNOWN'.")
    reasoning: str = Field(description="Brief explanation of why this intent was chosen.")

class ReportSynthesis(BaseModel):
    risk_level: str = Field(description="The final risk level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'")
    confidence: str = Field(description="Confidence score between 0.00 and 1.00 as a string")
    actions: list[str] = Field(description="List of recommended actions, e.g., 'Escalate to L2', 'File SAR', 'Monitor'")
    summary: str = Field(description="A concise executive summary of the evidence and justification for the risk level.")

def supervisor_agent(state: AgentState):
    messages = state.get("messages", [])
    last_user_msg = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    ).lower()

    start_time = time.time()
    
    # Actual LLM Intent Parsing
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        structured_llm = llm.with_structured_output(SupervisorIntent)
        
        prompt = f"""
        You are an AML investigation supervisor. Analyze the following user request and extract the customer ID and the intent.
        The intent must be one of:
        - 'structuring': if the user mentions structuring, velocity, splitting payments, avoiding reporting thresholds.
        - 'threshold': if the user mentions absolute dollar limits (e.g. >$10,000, 10+ transactions).
        - 'single_entity': if the user just asks to investigate a specific customer or asks generally about suspicion without mentioning specific AML patterns.
        
        User request: {last_user_msg}
        """
        
        result: SupervisorIntent = structured_llm.invoke(prompt)
        intent = result.intent
        customer_id = result.customer_id
        reasoning = result.reasoning
    except Exception as e:
        # Fallback if API key is missing or LLM fails
        intent = "single_entity"
        reasoning = f"LLM Parsing failed ({str(e)}). Default deep-dive."
        match = re.search(r'c_\d+', last_user_msg, re.IGNORECASE)
        if match:
            customer_id = match.group(0).upper()

    execution_plan = {
        "structuring": ["isolation_forest_tool", "hybrid_risk_tool"],
        "threshold": ["rule_engine_tool", "hybrid_risk_tool"],
        "single_entity": [
            "customer_360_tool",
            "transaction_tool",
            "timeline_tool",
            "rule_engine_tool",
            "isolation_forest_tool",
            "hybrid_risk_tool",
        ],
    }.get(intent, [])
    
    duration = round(time.time() - start_time, 2)
    
    log = ActionLog(
        timestamp=get_current_time(),
        tool="Lead AI Investigator",
        duration=duration,
        result=f"Rule-based intent parsed: '{intent}' for {customer_id}. Reason: {reasoning}",
        status="COMPLETED",
    )
    
    return {
        "current_intent": intent, 
        "customer_id": customer_id, 
        "execution_plan": execution_plan,
        "planner_timeline": [log]
    }

def router(state: AgentState) -> str:
    """Routes execution based on the supervisor's parsed intent."""
    intent = state.get("current_intent", "single_entity")
    if intent == "structuring":
        return "ml_intelligence_agent"
    elif intent == "threshold":
        return "rule_intelligence_agent"
    else:
        return "customer_agent"

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
    res = _run_agent_tool("Entity Linkage Analyzer", "timeline_tool", customer_id) # Using timeline_tool as proxy for network hops
    return {"planner_timeline": [res["log"]], "messages": [AIMessage(content=f"Network Agent Results: {json.dumps([res])}")]}

def rule_intelligence_agent(state: AgentState):
    """Standalone Rule Intelligence Agent — runs deterministic AML rules only."""
    customer_id = state.get("customer_id", "UNKNOWN")
    res = _run_agent_tool("Regulatory Rules Engine", "rule_engine_tool", customer_id)
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
    res = _run_agent_tool("Behavioral Analytics Engine", "isolation_forest_tool", customer_id)
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
    res = _run_agent_tool("Compliance Policy Engine", "hybrid_risk_tool", customer_id)
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
    
    log = ActionLog(timestamp=get_current_time(), tool="Dossier Compiler", duration=0.05, result=f"Built structured evidence graph with {len(evidence)} items.", status="COMPLETED")
    return {"evidence_bundle": evidence, "planner_timeline": [log],
            "messages": [AIMessage(content=f"Evidence Graph: {json.dumps(evidence_graph)}")]}

def report_generator_agent(state: AgentState):
    evidence = state.get("evidence_bundle", [])
    messages = state.get("messages", [])
    intent = state.get("current_intent", "single_entity")
    
    # Extract evidence strings for context
    evidence_text = "\n".join([f"{e['title']}: {e['description']} (Severity: {e['severity']})" for e in evidence])
    
    # Actual LLM Report Synthesis
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        structured_llm = llm.with_structured_output(ReportSynthesis)
        
        prompt = f"""
        You are the Chief Compliance AI. Review the following gathered evidence and synthesize a final Suspicious Activity Report (SAR) recommendation.
        
        Intent: {intent}
        
        Evidence Gathered:
        {evidence_text}
        
        Determine the overall risk_level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'), a confidence score, the recommended actions, and a concise executive summary explaining your decision.
        """
        
        result: ReportSynthesis = structured_llm.invoke(prompt)
        risk_level = result.risk_level
        confidence = result.confidence
        actions = result.actions
        summary = result.summary
    except Exception as e:
        # Fallback if API key is missing or LLM fails
        risk_level = "HIGH" if any(e['severity'] == "HIGH" for e in evidence) else "LOW"
        confidence = "0.85"
        actions = ["Escalate to L2"] if risk_level == "HIGH" else ["Monitor"]
        summary = f"LLM Synthesis failed ({str(e)}). Default fallback reasoning applied based on evidence severity."

    rec_dict = Recommendation(risk_level=risk_level, confidence=confidence, evidence_count=len(evidence), recommended_actions=actions)
    log = ActionLog(timestamp=get_current_time(), tool="SAR Synthesizer", duration=1.5, result=f"Generated SAR/Report via LLM: {risk_level}", status="COMPLETED")

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
    
    # Store to SQLite Database
    try:
        db = SessionLocal()
        new_audit = DBAuditLog(
            customer_id=customer_id,
            total_actions=len(timeline),
            actions_json=json.dumps(audit_record)
        )
        db.add(new_audit)
        db.commit()
    except Exception as e:
        print(f"Error saving to Audit Log DB: {e}")
    finally:
        db.close()
        
    log = ActionLog(
        timestamp=get_current_time(),
        tool="Compliance Audit Logger",
        duration=0.01,
        result=f"Audit trail created for {customer_id}: {len(timeline)} actions logged to SQLite Database.",
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
# Conditional Routing from Supervisor
builder.add_conditional_edges("supervisor_agent", router, {
    "ml_intelligence_agent": "ml_intelligence_agent",
    "rule_intelligence_agent": "rule_intelligence_agent",
    "customer_agent": "customer_agent"
})

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
