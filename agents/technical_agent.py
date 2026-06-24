"""
Technical Agent — handles technical issues (crashes, bugs, performance).

Searches the knowledge base and reviews ticket history to determine whether
the issue is a known bug or needs escalation.
"""

import json
from tools.knowledge_base import search_knowledge_base
from tools.ticket_history import get_ticket_history
from agents.llm_helper import invoke_llm_with_fallback


def technical_agent(state: dict) -> dict:
    """Analyse a technical issue and check for known bugs."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running technical_agent for ticket {ticket_id}")

    # ── Tool calls ───────────────────────────────────────────────────
    kb_results = search_knowledge_base.invoke({"query": f"crash performance {message}"})
    ticket_history = get_ticket_history.invoke({"customer_id": customer_id})

    tools_used = list(state.get("tools_used", []))
    tools_used.extend(["search_knowledge_base", "get_ticket_history"])

    routing_path = list(state.get("routing_path", []))
    routing_path.append("technical_agent")

    # ── LLM analysis ────────────────────────────────────────────────
    prompt = f"""You are a technical support specialist.

CUSTOMER MESSAGE:
{message}

KNOWLEDGE BASE RESULTS:
{json.dumps(kb_results, indent=2)}

TICKET HISTORY:
{json.dumps(ticket_history, indent=2)}

CUSTOMER INFO:
{json.dumps(state.get("customer_info", {}), indent=2)}

Analyse the technical issue:
1. Is this a known bug with a documented fix?
2. Has the customer reported similar issues before?
3. Is the business impact severe enough to warrant escalation?
If the customer mentions losing business, revenue impact, or inability to work, set escalation_required to true.
4. What resolution steps can you provide?

IMPORTANT: Never include placeholder text like [insert X] or [example] in your resolution. Write the complete response.

Respond with ONLY valid JSON (no markdown fences):
{{
  "agent_notes": "<your technical analysis>",
  "resolution": "<proposed resolution or troubleshooting steps>",
  "escalation_required": <true or false>,
  "escalation_reason": "<reason or empty string>"
}}"""

    try:
        result = invoke_llm_with_fallback("technical_agent", prompt, state)

        agent_notes = result.get("agent_notes", "Technical issue reviewed.")
        resolution = result.get("resolution", "Please try standard troubleshooting steps.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")

    except Exception as e:
        print(f"[AGENT] technical_agent error: {e}")
        agent_notes = "Technical issue received; LLM analysis unavailable."
        resolution = "Our engineering team will investigate this issue."
        escalation_required = True
        escalation_reason = "LLM failure — defaulting to escalation for safety."

    # Also escalate if confidence is too low
    confidence = state.get("confidence_score", 0.7)
    if confidence < 0.6:
        escalation_required = True
        escalation_reason = escalation_reason or "Low triage confidence — escalating for review."

    return {
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "ticket_history": ticket_history,
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
