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

def analyze_intent(state: AgentState):
    messages = state.get("messages", [])
    last_user_msg = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    )

    # Deterministic intent extraction
    # Look for C_XXXX pattern
    customer_id = state.get("customer_id", "UNKNOWN")
    match = re.search(r'C_\d+', last_user_msg, re.IGNORECASE)
    if match:
        customer_id = match.group(0).upper()

    intent = f"Investigate customer {customer_id}"

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Deterministic Intent Analyzer",
        duration=0.01,
        result=intent,
        status="COMPLETED",
    )

    return {
        "current_intent": intent,
        "customer_id": customer_id,
        "planner_timeline": [log],
    }

def generate_plan(state: AgentState):
    # Deterministically run all available tools
    plan = [
        "customer_360_tool", 
        "transaction_tool", 
        "rule_engine_tool", 
        "isolation_forest_tool", 
        "hybrid_risk_tool", 
        "timeline_tool"
    ]

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Deterministic Planner",
        duration=0.01,
        result=f"Generated plan with {len(plan)} core tools.",
        status="COMPLETED",
    )

    return {"execution_plan": plan, "planner_timeline": [log]}

def execute_tools(state: AgentState):
    plan = state.get("execution_plan", [])
    customer_id = state.get("customer_id", "UNKNOWN")

    results = []
    logs = []

    for tool_name in plan:
        tool_func = get_tool_by_name(tool_name)
        if tool_func:
            start_time = time.time()
            try:
                # Tools currently expect customer_id
                res = tool_func.invoke({"customer_id": customer_id})
                duration = time.time() - start_time
                results.append({"tool": tool_name, "output": res})
                logs.append(
                    ActionLog(
                        timestamp=get_current_time(),
                        tool=tool_name,
                        duration=round(duration, 2),
                        result="Success",
                        status="COMPLETED",
                    )
                )
            except Exception as e:
                duration = time.time() - start_time
                results.append({"tool": tool_name, "output": f"Error: {str(e)}"})
                logs.append(
                    ActionLog(
                        timestamp=get_current_time(),
                        tool=tool_name,
                        duration=round(duration, 2),
                        result="Failed",
                        status="FAILED",
                    )
                )
        else:
            logs.append(
                ActionLog(
                    timestamp=get_current_time(),
                    tool=tool_name,
                    duration=0.01,
                    result="Tool Not Found",
                    status="FAILED",
                )
            )

    raw_output = json.dumps(results)

    return {
        "planner_timeline": logs,
        "messages": [AIMessage(content=f"Tool Execution Results: {raw_output}")],
    }

def aggregate_evidence(state: AgentState):
    messages = state.get("messages", [])
    tool_results_str = next(
        (
            m.content
            for m in reversed(messages)
            if isinstance(m, AIMessage)
            and m.content.startswith("Tool Execution Results:")
        ),
        "",
    )
    
    # Deterministic evidence aggregation
    evidence_list = []
    try:
        raw_json = tool_results_str.replace("Tool Execution Results: ", "")
        results = json.loads(raw_json)
        for res in results:
            tool_name = res.get("tool", "Unknown")
            output = str(res.get("output", ""))
            
            # Simple heuristic extraction
            if "rule_engine" in tool_name and "Triggered" in output:
                evidence_list.append(EvidenceItem(source="Rule Engine", description="Customer triggered specific AML rules."))
            if "isolation_forest" in tool_name and "score" in output.lower():
                evidence_list.append(EvidenceItem(source="Anomaly Detection", description="Isolation Forest anomaly score generated."))
            if "hybrid_risk" in tool_name:
                evidence_list.append(EvidenceItem(source="Hybrid Risk", description="Composite risk profile calculated."))
                
    except Exception as e:
        evidence_list.append(EvidenceItem(source="Aggregator", description="Failed to parse detailed evidence."))
        
    if not evidence_list:
        evidence_list.append(EvidenceItem(source="System", description="General activity retrieved successfully."))

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Deterministic Aggregator",
        duration=0.05,
        result=f"Extracted {len(evidence_list)} evidence items.",
        status="COMPLETED",
    )

    return {"evidence_bundle": evidence_list, "planner_timeline": [log]}

def generate_recommendation(state: AgentState):
    evidence = state.get("evidence_bundle", [])
    messages = state.get("messages", [])
    
    # Simple deterministic risk logic
    risk_level = "LOW"
    confidence = "90%"
    actions = ["Monitor"]
    summary = "No immediate threat detected. Automated monitoring will continue."
    
    # Extract hybrid score from previous tool results if possible
    tool_results_str = next(
        (m.content for m in reversed(messages) if isinstance(m, AIMessage) and m.content.startswith("Tool Execution Results:")), ""
    )
    
    if "CRITICAL" in tool_results_str or "HIGH" in tool_results_str:
        risk_level = "HIGH"
        confidence = "85%"
        actions = ["Escalate to L2", "File SAR"]
        summary = "Deterministic engine detected high-risk indicators based on composite scoring."
    elif "MEDIUM" in tool_results_str:
        risk_level = "MEDIUM"
        confidence = "80%"
        actions = ["Manual Review"]
        summary = "Deterministic engine detected moderate risk. Proceed with manual review."

    rec_dict = Recommendation(
        risk_level=risk_level,
        confidence=confidence,
        evidence_count=len(evidence),
        recommended_actions=actions,
    )

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Deterministic Recommendation",
        duration=0.01,
        result=f"Recommendation: {risk_level}",
        status="COMPLETED",
    )

    return {
        "final_recommendation": rec_dict,
        "messages": [AIMessage(content=summary)],
        "planner_timeline": [log],
    }

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("analyze_intent", analyze_intent)
builder.add_node("generate_plan", generate_plan)
builder.add_node("execute_tools", execute_tools)
builder.add_node("aggregate_evidence", aggregate_evidence)
builder.add_node("generate_recommendation", generate_recommendation)

builder.add_edge(START, "analyze_intent")
builder.add_edge("analyze_intent", "generate_plan")
builder.add_edge("generate_plan", "execute_tools")
builder.add_edge("execute_tools", "aggregate_evidence")
builder.add_edge("aggregate_evidence", "generate_recommendation")
builder.add_edge("generate_recommendation", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

def get_agent_executor():
    return graph
