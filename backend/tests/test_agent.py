import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage
from app.agent.graph import get_agent_executor, IntentAnalysis, ExecutionPlan, AggregatedEvidence, FinalRecommendation

@pytest.fixture
def mock_llm():
    with patch("app.agent.graph.get_llm") as mock_get_llm:
        mock_instance = MagicMock()
        mock_get_llm.return_value = mock_instance
        
        # Mock structured output for different intents based on node
        def mock_structured_output(schema):
            mock_structured_instance = MagicMock()
            if schema == IntentAnalysis:
                mock_structured_instance.invoke.return_value = IntentAnalysis(intent="Investigate CUST-123", customer_id="CUST-123")
            elif schema == ExecutionPlan:
                mock_structured_instance.invoke.return_value = ExecutionPlan(tools_to_run=["transaction_tool"])
            elif schema == AggregatedEvidence:
                mock_structured_instance.invoke.return_value = AggregatedEvidence(evidence=[{"source": "test", "description": "test evidence"}])
            elif schema == FinalRecommendation:
                mock_structured_instance.invoke.return_value = FinalRecommendation(
                    risk_level="HIGH", confidence="90%", evidence_count=1, recommended_actions=["File SAR"], summary="Test summary"
                )
            return mock_structured_instance
            
        mock_instance.with_structured_output.side_effect = mock_structured_output
        yield mock_get_llm

def test_analyze_intent(mock_llm):
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_1"}}
    input_message = HumanMessage(content="Investigate customer CUST-001 for money laundering")
    
    result = agent_executor.invoke({"messages": [input_message], "customer_id": "CUST-001"}, config=config)
    
    assert "current_intent" in result
    assert result["current_intent"] == "Investigate CUST-123"

def test_dynamic_plan(mock_llm):
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_2"}}
    input_message = HumanMessage(content="Check if CUST-123 has suspicious transactions.")
    
    result = agent_executor.invoke({"messages": [input_message], "customer_id": "CUST-123"}, config=config)
    
    plan = result.get("execution_plan", [])
    assert len(plan) == 1
    assert "transaction_tool" in plan

def test_memory_persistence(mock_llm):
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_3"}}
    
    input_message = HumanMessage(content="Hello, my customer is CUST-999")
    agent_executor.invoke({"messages": [input_message], "customer_id": "CUST-999"}, config=config)
    
    followup_message = HumanMessage(content="What was the customer ID again?")
    result = agent_executor.invoke({"messages": [followup_message]}, config=config)
    
    # Check that it retained messages
    messages = result.get("messages", [])
    assert len(messages) >= 2

def test_evidence_aggregation(mock_llm):
    agent_executor = get_agent_executor()
    config = {"configurable": {"thread_id": "test_thread_4"}}
    input_message = HumanMessage(content="Run full check on CUST-555")
    
    result = agent_executor.invoke({"messages": [input_message], "customer_id": "CUST-555"}, config=config)
    
    evidence = result.get("evidence_bundle", [])
    assert isinstance(evidence, list)
    
    recommendation = result.get("final_recommendation", {})
    assert recommendation.get("risk_level") == "HIGH"
    assert len(recommendation.get("recommended_actions", [])) > 0
