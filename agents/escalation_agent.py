"""
Escalation Agent — produces a detailed escalation summary for human agents.

Only runs when escalation_required == True. Generates a structured
summary including customer info, issue details, what was tried, and
recommended next steps.
"""

import json
from agents.llm_helper import invoke_llm_with_fallback


def escalation_agent(state: dict) -> dict:
    """Write a detailed escalation summary for human agents."""
    ticket_id = state.get("ticket_id", "UNKNOWN")

    print(f"[AGENT] Running escalation_agent for ticket {ticket_id}")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("escalation_agent")

    prompt = f"""You are an escalation specialist. Write a detailed escalation summary.

TICKET ID: {ticket_id}
CUSTOMER INFO: {json.dumps(state.get("customer_info", {}), indent=2)}
CATEGORY: {state.get("category", "Unknown")}
PRIORITY: {state.get("priority", "medium")}
ORIGINAL MESSAGE: {state.get("message", "")}
AGENT NOTES: {state.get("agent_notes", "")}
RESOLUTION ATTEMPTED: {state.get("resolution", "")}
ESCALATION REASON: {state.get("escalation_reason", "")}

Write a structured escalation summary with:
1. Customer overview
2. Issue summary
3. What was attempted
4. Why escalation is needed
5. Recommended next steps
6. Priority level

Respond with ONLY valid JSON:
{{
  "escalation_notes": "<full escalation summary>",
  "escalation_reason": "<concise reason>"
}}"""

    try:
        result = invoke_llm_with_fallback("escalation_agent", prompt, state)
        escalation_notes = result.get("escalation_notes", "Escalation summary unavailable.")
        escalation_reason = result.get("escalation_reason", state.get("escalation_reason", ""))
    except Exception as e:
        print(f"[AGENT] escalation_agent error: {e}")
        escalation_notes = (
            f"ESCALATION SUMMARY\n"
            f"Ticket: {ticket_id}\n"
            f"Category: {state.get('category', 'Unknown')}\n"
            f"Priority: {state.get('priority', 'medium')}\n"
            f"Reason: {state.get('escalation_reason', 'Unknown')}\n"
            f"Notes: {state.get('agent_notes', 'N/A')}"
        )
        escalation_reason = state.get("escalation_reason", "Requires human review.")

    # BONUS: print escalation summary to console (simulating email/Telegram)
    print("\n" + "=" * 60)
    print("!!! ESCALATION NOTIFICATION (simulated email/Telegram) !!!")
    print("=" * 60)
    print(escalation_notes)
    print("=" * 60 + "\n")

    return {
        "escalation_notes": escalation_notes,
        "escalation_reason": escalation_reason,
        "routing_path": routing_path,
    }
