"""
Triage Agent — classifies the ticket category, priority, and confidence.

This is the entry-point agent. It enriches state with customer info and
ticket history, then asks the LLM to classify the ticket.
"""

import json
from tools.customer_lookup import lookup_customer
from tools.ticket_history import get_ticket_history
from agents.llm_helper import invoke_llm_with_fallback

VALID_CATEGORIES = [
    "Billing",
    "Technical Issue",
    "Feature Request",
    "General Inquiry",
    "Account Management",
]

VALID_PRIORITIES = ["low", "medium", "high", "critical"]


def triage_agent(state: dict) -> dict:
    """Classify the incoming ticket and enrich state with customer data."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running triage_agent for ticket {ticket_id}")

    # ── Tool calls ───────────────────────────────────────────────────
    customer_info = lookup_customer.invoke({"customer_id": customer_id})
    ticket_history = get_ticket_history.invoke({"customer_id": customer_id})

    tools_used = list(state.get("tools_used", []))
    tools_used.extend(["lookup_customer", "get_ticket_history"])

    routing_path = list(state.get("routing_path", []))
    routing_path.append("triage_agent")

    # ── LLM classification ───────────────────────────────────────────
    prompt = f"""You are a customer support triage specialist.

Classify the following customer support ticket.

CUSTOMER INFO:
{json.dumps(customer_info, indent=2)}

TICKET HISTORY:
{json.dumps(ticket_history, indent=2)}

CUSTOMER MESSAGE:
{message}

Classify the ticket into EXACTLY ONE of these categories:
{json.dumps(VALID_CATEGORIES)}

Assign a priority from: {json.dumps(VALID_PRIORITIES)}
- "low": general questions, feature requests
- "medium": billing inquiries, minor issues
- "high": service disruptions, repeated issues
- "critical": security concerns, data loss, major outages

Assign a confidence_score between 0.0 and 1.0 for how confident you are.

Respond with ONLY valid JSON (no markdown fences):
{{
  "category": "<category>",
  "priority": "<priority>",
  "confidence_score": <float>,
  "reasoning": "<brief reasoning>"
}}"""

    try:
        result = invoke_llm_with_fallback("triage_agent", prompt, state)

        category = result.get("category", "General Inquiry")
        if category not in VALID_CATEGORIES:
            category = "General Inquiry"

        priority = result.get("priority", "medium")
        if priority not in VALID_PRIORITIES:
            priority = "medium"

        confidence_score = float(result.get("confidence_score", 0.7))
        confidence_score = max(0.0, min(1.0, confidence_score))

    except Exception as e:
        print(f"[AGENT] triage_agent error: {e}")
        category = "General Inquiry"
        priority = "medium"
        confidence_score = 0.5

    return {
        "category": category,
        "priority": priority,
        "confidence_score": confidence_score,
        "customer_info": customer_info,
        "ticket_history": ticket_history,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
