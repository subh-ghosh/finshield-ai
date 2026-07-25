import json
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import time
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from app.agent.state import AgentState, EvidenceItem, Recommendation, ActionLog
from app.agent.tools import get_tool_by_name


# Initialize LLM lazily
def get_llm():
    try:
        return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    except Exception:
        return None


# Structured Output Models
class IntentAnalysis(BaseModel):
    intent: str = Field(description="The user's intent or primary objective.")
    customer_id: str = Field(
        default="UNKNOWN",
        description="The customer ID if mentioned, otherwise UNKNOWN.",
    )


class ExecutionPlan(BaseModel):
    tools_to_run: list[str] = Field(
        description="List of tool names to execute. e.g. ['transaction_tool', 'rule_engine_tool']"
    )


class AggregatedEvidence(BaseModel):
    evidence: list[dict] = Field(
        description="List of evidence items with 'source' and 'description'."
    )


class FinalRecommendation(BaseModel):
    risk_level: str = Field(description="e.g., LOW, MEDIUM, HIGH, CRITICAL")
    confidence: str = Field(description="e.g., 95%")
    evidence_count: int = Field(description="Number of distinct evidence items")
    recommended_actions: list[str] = Field(
        description="e.g., ['File SAR', 'Freeze Account']"
    )
    summary: str = Field(description="A brief explanation.")


def get_current_time():
    return datetime.utcnow().isoformat()


def analyze_intent(state: AgentState):
    messages = state.get("messages", [])
    last_user_msg = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    )

    prompt = f"Analyze this user query for an AML investigation. Query: {last_user_msg}"
    structured_llm = get_llm().with_structured_output(IntentAnalysis)
    result = structured_llm.invoke(
        [
            SystemMessage(content="You are an expert AML intent analyzer."),
            HumanMessage(content=prompt),
        ]
    )

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Intent Analyzer",
        duration=0.5,
        result=result.intent,
        status="COMPLETED",
    )

    cust_id = (
        result.customer_id
        if result.customer_id != "UNKNOWN"
        else state.get("customer_id", "UNKNOWN")
    )

    return {
        "current_intent": result.intent,
        "customer_id": cust_id,
        "planner_timeline": [log],
    }


def generate_plan(state: AgentState):
    intent = state.get("current_intent", "")
    prompt = f"Based on the intent '{intent}', which tools should be run? Available tools: customer_360_tool, transaction_tool, rule_engine_tool, isolation_forest_tool, hybrid_risk_tool, timeline_tool."

    structured_llm = get_llm().with_structured_output(ExecutionPlan)
    result = structured_llm.invoke(
        [
            SystemMessage(
                content="You are an AML execution planner. Return a minimal list of tools needed. Do not include unnecessary tools."
            ),
            HumanMessage(content=prompt),
        ]
    )

    plan = result.tools_to_run

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Execution Planner",
        duration=0.8,
        result=f"Generated plan with {len(plan)} tools.",
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
                    duration=0.1,
                    result="Tool Not Found",
                    status="FAILED",
                )
            )

    # We store the raw tool outputs in messages as AIMessages for now,
    # so aggregate_evidence can read them, or pass them in a temporary state key.
    # Let's pass them via a generic message.
    raw_output = json.dumps(results)

    return {
        "planner_timeline": logs,
        "messages": [AIMessage(content=f"Tool Execution Results: {raw_output}")],
    }


def aggregate_evidence(state: AgentState):
    messages = state.get("messages", [])
    # Find the tool execution results message
    tool_results = next(
        (
            m.content
            for m in reversed(messages)
            if isinstance(m, AIMessage)
            and m.content.startswith("Tool Execution Results:")
        ),
        "",
    )

    prompt = f"Extract structured evidence from these tool results: {tool_results}"
    structured_llm = get_llm().with_structured_output(AggregatedEvidence)
    result = structured_llm.invoke(
        [
            SystemMessage(
                content="You are an AML evidence aggregator. Extract key facts into a structured list."
            ),
            HumanMessage(content=prompt),
        ]
    )

    evidence_list = [
        EvidenceItem(
            source=e.get("source", "Unknown"), description=e.get("description", "None")
        )
        for e in result.evidence
    ]

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Evidence Aggregator",
        duration=1.2,
        result=f"Extracted {len(evidence_list)} evidence items.",
        status="COMPLETED",
    )

    return {"evidence_bundle": evidence_list, "planner_timeline": [log]}


def generate_recommendation(state: AgentState):
    evidence = state.get("evidence_bundle", [])
    intent = state.get("current_intent", "")

    evidence_text = "\n".join(
        [f"- {e['source']}: {e['description']}" for e in evidence]
    )
    prompt = f"Intent: {intent}\n\nEvidence:\n{evidence_text}\n\nGenerate a final recommendation."

    structured_llm = get_llm().with_structured_output(FinalRecommendation)
    result = structured_llm.invoke(
        [
            SystemMessage(
                content="You are a Senior AML Investigator producing a final risk assessment."
            ),
            HumanMessage(content=prompt),
        ]
    )

    rec_dict = Recommendation(
        risk_level=result.risk_level,
        confidence=result.confidence,
        evidence_count=result.evidence_count,
        recommended_actions=result.recommended_actions,
    )

    log = ActionLog(
        timestamp=get_current_time(),
        tool="Recommendation Engine",
        duration=1.5,
        result=f"Recommendation: {result.risk_level}",
        status="COMPLETED",
    )

    return {
        "final_recommendation": rec_dict,
        "messages": [AIMessage(content=result.summary)],
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
