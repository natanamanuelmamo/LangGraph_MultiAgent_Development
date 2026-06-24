"""
Technical Agent — handles technical issues (crashes, bugs, performance).

UPGRADED: Uses dynamic tool selection — the LLM decides which tools
to call based on the ticket content.
"""

import json
from agents.llm_helper import get_llm, invoke_llm_with_fallback
from agents.smart_tool_caller import run_with_dynamic_tools, parse_json_safe
from tools.tool_registry import TECHNICAL_TOOLS


def technical_agent(state: dict) -> dict:
    """Analyse a technical issue using dynamic tool selection."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    customer_id = state.get("customer_id", "UNKNOWN")
    message = state.get("message", "")

    print(f"[AGENT] Running technical_agent for ticket {ticket_id}")
    print(f"[AGENT] Available tools: {[t.name for t in TECHNICAL_TOOLS]}")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("technical_agent")

    tools_used = list(state.get("tools_used", []))

    # ── Dynamic tool selection ───────────────────────────────────────
    system_prompt = """You are a technical support specialist.
    Diagnose technical issues and decide which tools you need 
    to gather relevant information."""

    user_message = f"""Customer ID: {customer_id}
Customer Message: {message}
Customer Info: {json.dumps(state.get("customer_info", {}))}

Decide which tools to call to diagnose this technical issue.
Consider: Is this a known bug? Has the customer had similar issues before?"""

    tool_results, dynamic_tools_used = run_with_dynamic_tools(
        agent_name="technical_agent",
        system_prompt=system_prompt,
        user_message=user_message,
        available_tools=TECHNICAL_TOOLS,
        state=state,
    )

    tools_used.extend(dynamic_tools_used)

    kb_results = tool_results.get("search_knowledge_base", {})
    ticket_history = tool_results.get("get_ticket_history", [])

    # ── LLM analysis with gathered data ─────────────────────────────
    analysis_prompt = f"""You are a technical support specialist.

CUSTOMER MESSAGE:
{message}

TOOLS SELECTED AND RESULTS:
{json.dumps(tool_results, indent=2)}

CUSTOMER INFO:
{json.dumps(state.get("customer_info", {}), indent=2)}

Analyse the technical issue:
1. Is this a known bug with a documented fix?
2. Has the customer reported similar issues before?
3. Is the business impact severe enough to warrant escalation?
   If the customer mentions losing business or revenue impact, set escalation_required to true.
4. What resolution steps can you provide?

IMPORTANT: Never include placeholder text like [insert X] in your resolution.

Respond with ONLY valid JSON (no markdown fences):
{{
  "agent_notes": "<your technical analysis>",
  "resolution": "<proposed resolution or troubleshooting steps>",
  "escalation_required": <true or false>,
  "escalation_reason": "<reason or empty string>"
}}"""

    try:
        result = invoke_llm_with_fallback("technical_agent", analysis_prompt, state)
        agent_notes = result.get("agent_notes", "Technical issue reviewed.")
        resolution = result.get("resolution", "Our team will investigate.")
        escalation_required = bool(result.get("escalation_required", False))
        escalation_reason = result.get("escalation_reason", "")
    except Exception as e:
        print(f"[AGENT] technical_agent analysis error: {e}")
        agent_notes = "Technical issue received; analysis unavailable."
        resolution = "Our engineering team will investigate this issue."
        escalation_required = True
        escalation_reason = "Analysis failed — defaulting to escalation for safety."

    confidence = state.get("confidence_score", 0.7)
    if confidence < 0.6:
        escalation_required = True
        escalation_reason = escalation_reason or "Low triage confidence — escalating for review."

    return {
        "knowledge_base_results": kb_results.get("results", []) if isinstance(kb_results, dict) else [],
        "ticket_history": ticket_history if isinstance(ticket_history, list) else [],
        "agent_notes": agent_notes,
        "resolution": resolution,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "tools_used": tools_used,
        "routing_path": routing_path,
    }
