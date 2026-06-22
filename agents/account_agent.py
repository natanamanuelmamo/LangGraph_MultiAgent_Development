"""
Account Agent — handles account management issues.

Covers password resets, 2FA, cancellation, and security concerns.
Security issues (2FA, breach, hacking) ALWAYS trigger escalation.
"""

import json
from tools.customer_lookup import lookup_customer
from tools.knowledge_base import search_knowledge_base
from agents.llm_helper import invoke_llm_with_fallback

SECURITY_KEYWORDS = [
    "hack", "hacked", "breach", "unauthorized",
    "2fa", "two-factor", "compromised", "stolen", "suspicious",
]


def account_agent(state: dict) -> dict:
    """Handle account management issues with special attention to security."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running account_agent for ticket {ticket_id}")

    customer_info = lookup_customer.invoke({"customer_id": customer_id})
    kb_results = search_knowledge_base.invoke({"query": f"password two-factor cancel {message}"})

    tools_used = list(state.get("tools_used", []))
    tools_used.extend(["lookup_customer", "search_knowledge_base"])

    routing_path = list(state.get("routing_path", []))
    routing_path.append("account_agent")

    message_lower = message.lower()
    is_security_issue = any(kw in message_lower for kw in SECURITY_KEYWORDS)

    prompt = f"""You are an account management specialist.

CUSTOMER MESSAGE:
{message}

CUSTOMER INFO:
{json.dumps(customer_info, indent=2)}

KNOWLEDGE BASE RESULTS:
{json.dumps(kb_results, indent=2)}

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
        result = invoke_llm_with_fallback("account_agent", prompt, state)
        agent_notes = result.get("agent_notes", "Account issue reviewed.")
        resolution = result.get("resolution", "Please contact account support.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")
    except Exception as e:
        print(f"[AGENT] account_agent error: {e}")
        agent_notes = "Account issue received; LLM analysis unavailable."
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
