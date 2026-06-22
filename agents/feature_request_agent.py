"""
Feature Request Agent — acknowledges feature requests and logs them.

Feature requests are never auto-escalated. The agent checks the knowledge
base for existing/planned features and responds with an acknowledgement.
"""

import json
from tools.knowledge_base import search_knowledge_base
from agents.llm_helper import invoke_llm_with_fallback


def feature_request_agent(state: dict) -> dict:
    """Acknowledge a feature request and provide a roadmap-style response."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running feature_request_agent for ticket {ticket_id}")

    # ── Tool calls ───────────────────────────────────────────────────
    kb_results = search_knowledge_base.invoke({"query": message})

    tools_used = list(state.get("tools_used", []))
    tools_used.append("search_knowledge_base")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("feature_request_agent")

    # ── LLM analysis ────────────────────────────────────────────────
    prompt = f"""You are a product feedback specialist.

CUSTOMER MESSAGE:
{message}

KNOWLEDGE BASE RESULTS:
{json.dumps(kb_results, indent=2)}

The customer has submitted a feature request. Your job is to:
1. Acknowledge the request warmly.
2. Check if the feature already exists or is on the roadmap.
3. Provide a thoughtful response that makes the customer feel heard.

Feature requests are NEVER escalated — always set escalation_required to false.

Respond with ONLY valid JSON (no markdown fences):
{{
  "agent_notes": "<your analysis of the feature request>",
  "resolution": "<acknowledgement message with roadmap info>"
}}"""

    try:
        result = invoke_llm_with_fallback("feature_request_agent", prompt, state)

        agent_notes = result.get("agent_notes", "Feature request noted.")
        resolution = result.get(
            "resolution",
            "Thank you for your feature request! We've logged it and our product team will review it.",
        )

    except Exception as e:
        print(f"[AGENT] feature_request_agent error: {e}")
        agent_notes = "Feature request received; LLM analysis unavailable."
        resolution = (
            "Thank you for your suggestion! We've recorded your feature request "
            "and our product team will evaluate it for a future release."
        )

    return {
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": False,  # Feature requests are never auto-escalated
        "escalation_reason": "",
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
