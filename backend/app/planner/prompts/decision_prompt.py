"""Decision node prompt template for routing between more tools vs. report generation."""

DECISION_PROMPT_TEMPLATE = """You are evaluating whether sufficient evidence has been gathered to conclude an AML investigation.

Customer ID: {customer_id}
Tools already called: {tool_history}
Iteration: {iteration}/{max_iterations}

Evidence collected so far:
{evidence_summary}

Reasoning steps so far:
{reasoning_steps}

DECISION RULES:
1. If overall_risk_score, severity, recommendation, and at least one evidence item are present — investigation is SUFFICIENT.
2. If critical information is missing (e.g., no risk score, no evidence) AND iterations remain — request more tools.
3. If max iterations reached — conclude with available evidence regardless.
4. Never request a tool that has already been called.

Available tools not yet called: {remaining_tools}

Respond with EXACTLY one of:
- "SUFFICIENT" — enough evidence to generate the final report
- "NEEDS_MORE:<tool_name>" — request one additional tool (e.g., "NEEDS_MORE:get_explanation")
"""
