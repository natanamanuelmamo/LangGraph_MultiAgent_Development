"""
Billing Agent — handles billing-related issues (charges, refunds, invoices).

UPGRADED: Uses dynamic tool selection — the LLM decides which tools
to call based on the ticket content rather than a hardcoded sequence.
"""

import json
from agents.llm_helper import get_llm, invoke_llm_with_fallback
from agents.smart_tool_caller import run_with_dynamic_tools, parse_json_safe
from tools.tool_registry import BILLING_TOOLS


def billing_agent(state: dict) -> dict:
    """Analyse a billing issue using dynamic tool selection."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running billing_agent for ticket {ticket_id}")
    print(f"[AGENT] Available tools: {[t.name for t in BILLING_TOOLS]}")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("billing_agent")

    tools_used = list(state.get("tools_used", []))

    # ── Dynamic tool selection ───────────────────────────────────────
    system_prompt = """You are a billing support specialist. 
    Analyze billing issues and decide which tools you need to gather information."""

    user_message = f"""Customer ID: {customer_id}
Customer Message: {message}
Customer Info: {json.dumps(state.get("customer_info", {}))}

Decide which tools to call to gather the information you need 
to resolve this billing issue."""

    tool_results, dynamic_tools_used = run_with_dynamic_tools(
        agent_name="billing_agent",
        system_prompt=system_prompt,
        user_message=user_message,
        available_tools=BILLING_TOOLS,
        state=state,
    )

    tools_used.extend(dynamic_tools_used)

    # Extract results from dynamic tool calls
    subscription_info = tool_results.get("lookup_subscription", {})
    kb_results = tool_results.get("search_knowledge_base", {})
    ticket_history = tool_results.get("get_ticket_history", [])

    # ── LLM analysis with gathered data ─────────────────────────────
    analysis_prompt = f"""You are a billing support specialist.

CUSTOMER MESSAGE:
{message}

TOOLS SELECTED AND RESULTS:
{json.dumps(tool_results, indent=2)}

CUSTOMER INFO:
{json.dumps(state.get("customer_info", {}), indent=2)}

Based on the information gathered, analyse the billing issue and decide:
1. What notes to record about the issue.
2. What resolution to propose to the customer.
3. Whether this needs escalation to a human agent (True/False).
4. If escalating, provide a reason.

Respond with ONLY valid JSON (no markdown fences):
{{
  "agent_notes": "<your analysis notes>",
  "resolution": "<proposed resolution for the customer>",
  "escalation_required": <true or false>,
  "escalation_reason": "<reason or empty string>"
}}"""

    try:
        result = invoke_llm_with_fallback("billing_agent", analysis_prompt, state)
        agent_notes = result.get("agent_notes", "Billing issue reviewed.")
        resolution = result.get("resolution", "Please contact billing support.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")
    except Exception as e:
        print(f"[AGENT] billing_agent analysis error: {e}")
        agent_notes = "Billing issue received; analysis unavailable."
        resolution = "Our billing team will review your account and follow up."
        escalation_required = False
        escalation_reason = ""

    return {
        "subscription_info": subscription_info,
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "ticket_history": ticket_history if isinstance(ticket_history, list) else [],
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
