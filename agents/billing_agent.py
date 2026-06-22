"""
Billing Agent — handles billing-related issues (charges, refunds, invoices).

Enriches state with subscription info and knowledge base results,
then uses the LLM to analyse the billing issue and propose a resolution.
"""

import json
from tools.subscription_lookup import lookup_subscription
from tools.knowledge_base import search_knowledge_base
from agents.llm_helper import invoke_llm_with_fallback


def billing_agent(state: dict) -> dict:
    """Analyse a billing issue and propose a resolution."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running billing_agent for ticket {ticket_id}")

    # ── Tool calls ───────────────────────────────────────────────────
    subscription_info = lookup_subscription.invoke({"customer_id": customer_id})
    kb_results = search_knowledge_base.invoke({"query": f"billing refund {message}"})

    tools_used = list(state.get("tools_used", []))
    tools_used.extend(["lookup_subscription", "search_knowledge_base"])

    routing_path = list(state.get("routing_path", []))
    routing_path.append("billing_agent")

    # ── LLM analysis ────────────────────────────────────────────────
    prompt = f"""You are a billing support specialist.

CUSTOMER MESSAGE:
{message}

SUBSCRIPTION INFO:
{json.dumps(subscription_info, indent=2)}

KNOWLEDGE BASE RESULTS:
{json.dumps(kb_results, indent=2)}

CUSTOMER INFO:
{json.dumps(state.get("customer_info", {}), indent=2)}

Analyse the billing issue and decide:
1. What notes to record about the issue.
2. What resolution to propose to the customer.
3. Whether this needs escalation to a human agent (True/False).
   - Escalate if the issue involves large amounts, fraud suspicion, or cannot be resolved automatically.
4. If escalating, provide a reason.

Respond with ONLY valid JSON (no markdown fences):
{{
  "agent_notes": "<your analysis notes>",
  "resolution": "<proposed resolution for the customer>",
  "escalation_required": <true or false>,
  "escalation_reason": "<reason or empty string>"
}}"""

    try:
        result = invoke_llm_with_fallback("billing_agent", prompt, state)

        agent_notes = result.get("agent_notes", "Billing issue reviewed.")
        resolution = result.get("resolution", "Please contact billing support.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")

    except Exception as e:
        print(f"[AGENT] billing_agent error: {e}")
        agent_notes = "Billing issue received; LLM analysis unavailable."
        resolution = "Our billing team will review your account and follow up."
        escalation_required = False
        escalation_reason = ""

    return {
        "subscription_info": subscription_info,
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
