"""
Account Agent — handles account management issues.

UPGRADED: Uses dynamic tool selection — the LLM decides which tools
to call. Security issues always trigger escalation.
"""

import json
from agents.llm_helper import get_llm, invoke_llm_with_fallback
from agents.smart_tool_caller import run_with_dynamic_tools
from tools.tool_registry import ACCOUNT_TOOLS

SECURITY_KEYWORDS = [
    "hack", "hacked", "breach", "unauthorized",
    "2fa", "two-factor", "compromised", "stolen", "suspicious",
]


def account_agent(state: dict) -> dict:
    """Handle account management using dynamic tool selection."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running account_agent for ticket {ticket_id}")
    print(f"[AGENT] Available tools: {[t.name for t in ACCOUNT_TOOLS]}")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("account_agent")

    tools_used = list(state.get("tools_used", []))

    message_lower = message.lower()
    is_security_issue = any(kw in message_lower for kw in SECURITY_KEYWORDS)

    # ── Dynamic tool selection ───────────────────────────────────────
    system_prompt = """You are an account management specialist.
    Handle account issues including passwords, 2FA, cancellations,
    and security concerns. Choose tools wisely based on the issue type."""

    user_message = f"""Customer ID: {customer_id}
Customer Message: {message}
Is Security Issue: {is_security_issue}

Decide which tools to call to handle this account issue."""

    tool_results, dynamic_tools_used = run_with_dynamic_tools(
        agent_name="account_agent",
        system_prompt=system_prompt,
        user_message=user_message,
        available_tools=ACCOUNT_TOOLS,
        state=state,
    )

    tools_used.extend(dynamic_tools_used)

    customer_info = tool_results.get("lookup_customer", state.get("customer_info", {}))
    kb_results = tool_results.get("search_knowledge_base", {})

    # ── LLM analysis ────────────────────────────────────────────────
    analysis_prompt = f"""You are an account management specialist.

CUSTOMER MESSAGE:
{message}

TOOLS SELECTED AND RESULTS:
{json.dumps(tool_results, indent=2)}

IS SECURITY ISSUE: {is_security_issue}

If this is a SECURITY issue, you MUST set escalation_required to true.

Respond with ONLY valid JSON:
{{
  "agent_notes": "<analysis>",
  "resolution": "<resolution>",
  "escalation_required": <true or false>,
  "escalation_reason": "<reason or empty string>"
}}"""

    try:
        result = invoke_llm_with_fallback("account_agent", analysis_prompt, state)
        agent_notes = result.get("agent_notes", "Account issue reviewed.")
        resolution = result.get("resolution", "Please contact account support.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")
    except Exception as e:
        print(f"[AGENT] account_agent error: {e}")
        agent_notes = "Account issue received; analysis unavailable."
        resolution = "Our account team will review your request."
        escalation_required = is_security_issue
        escalation_reason = "Security concern detected." if is_security_issue else ""

    if is_security_issue:
        escalation_required = True
        if not escalation_reason:
            escalation_reason = "Security-related account issue requires human review."

    return {
        "customer_info": customer_info,
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
