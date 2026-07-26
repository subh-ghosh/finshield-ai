import pytest
from langchain_core.messages import HumanMessage
from app.agent.graph import get_agent_executor

def test_analyze_intent():
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_1"}}
    input_message = HumanMessage(content="Investigate customer C_12345 for money laundering")
    
    result = agent_executor.invoke({"messages": [input_message], "customer_id": "UNKNOWN"}, config=config)
    
    assert "current_intent" in result
    assert result["current_intent"] == "Investigate customer C_12345"
    assert result["customer_id"] == "C_12345"

def test_dynamic_plan():
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_2"}}
    input_message = HumanMessage(content="Check if C_123 has suspicious transactions.")
    
    result = agent_executor.invoke({"messages": [input_message], "customer_id": "UNKNOWN"}, config=config)
    
    plan = result.get("execution_plan", [])
    assert len(plan) == 6
    assert "transaction_tool" in plan
    assert "isolation_forest_tool" in plan

def test_evidence_aggregation():
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_4"}}
    input_message = HumanMessage(content="Run full check on C_555")
    
    result = agent_executor.invoke({"messages": [input_message], "customer_id": "UNKNOWN"}, config=config)
    
    evidence = result.get("evidence_bundle", [])
    assert isinstance(evidence, list)
    
    recommendation = result.get("final_recommendation", {})
    assert recommendation.get("risk_level") in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert len(recommendation.get("recommended_actions", [])) > 0
