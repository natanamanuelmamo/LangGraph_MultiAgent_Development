"""
General Inquiry Agent — answers general questions about the product.

Escalates if the triage confidence score is below 0.6, indicating
the question may not have been correctly categorised.
"""

import json
from tools.knowledge_base import search_knowledge_base
from agents.llm_helper import invoke_llm_with_fallback


def general_inquiry_agent(state: dict) -> dict:
    """Answer a general question using the knowledge base."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running general_inquiry_agent for ticket {ticket_id}")

    # ── Tool calls ───────────────────────────────────────────────────
    kb_results = search_knowledge_base.invoke({"query": message})

    tools_used = list(state.get("tools_used", []))
    tools_used.append("search_knowledge_base")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("general_inquiry_agent")

    # ── LLM analysis ────────────────────────────────────────────────
    prompt = f"""You are a helpful customer support agent answering general questions.

CUSTOMER MESSAGE:
{message}

KNOWLEDGE BASE RESULTS:
{json.dumps(kb_results, indent=2)}

CUSTOMER INFO:
{json.dumps(state.get("customer_info", {}), indent=2)}

Provide a clear, helpful answer to the customer's question.
If the knowledge base doesn't have enough information, say so honestly.

Respond with ONLY valid JSON (no markdown fences):
{{
  "agent_notes": "<your notes>",
  "resolution": "<answer to the customer's question>",
  "escalation_required": <true or false>,
  "escalation_reason": "<reason or empty string>"
}}"""

    try:
        result = invoke_llm_with_fallback("general_inquiry_agent", prompt, state)

        agent_notes = result.get("agent_notes", "General inquiry reviewed.")
        resolution = result.get("resolution", "Please refer to our help center.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")

    except Exception as e:
        print(f"[AGENT] general_inquiry_agent error: {e}")
        agent_notes = "General inquiry received; LLM analysis unavailable."
        resolution = "Please visit our help center or contact support for assistance."
        escalation_required = False
        escalation_reason = ""

    # Escalate if triage confidence was low
    confidence = state.get("confidence_score", 0.7)
    if confidence < 0.6:
        escalation_required = True
        escalation_reason = f"Low triage confidence ({confidence}) — escalating for human review."

    return {
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
