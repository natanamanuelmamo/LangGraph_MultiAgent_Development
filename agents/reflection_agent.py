"""
Reflection Agent (BONUS) — reviews and improves the resolution or escalation notes.

Checks for clarity, completeness, tone, and actionability. Rewrites
the response if the quality is deemed insufficient.
"""

from agents.llm_helper import invoke_llm_with_fallback


def reflection_agent(state: dict) -> dict:
    """Review and optionally improve the resolution quality."""
    ticket_id = state.get("ticket_id", "UNKNOWN")

    print(f"[AGENT] Running reflection_agent for ticket {ticket_id}")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("reflection_agent")

    resolution = state.get("resolution", "")
    escalation_notes = state.get("escalation_notes", "")
    content_to_review = escalation_notes if state.get("escalation_required") else resolution

    prompt = f"""You are a quality assurance reviewer for customer support responses.

ORIGINAL CUSTOMER MESSAGE:
{state.get("message", "")}

CONTENT TO REVIEW:
{content_to_review}

CATEGORY: {state.get("category", "Unknown")}
ESCALATED: {state.get("escalation_required", False)}

Review the content for:
1. Clarity — Is it easy to understand?
2. Completeness — Does it address the customer's issue fully?
3. Tone — Is it professional and empathetic?
4. Actionability — Does it give clear next steps?

If the quality is good, keep the resolution as-is and provide positive feedback.
If the quality is poor, rewrite and improve it.

Respond with ONLY valid JSON:
{{
  "reflection_feedback": "<your review notes>",
  "improved_resolution": "<improved version or same as original>",
  "quality_score": "<good or needs_improvement>"
}}"""

    try:
        result = invoke_llm_with_fallback("reflection_agent", prompt, state)
        reflection_feedback = result.get("reflection_feedback", "Review complete.")
        improved = result.get("improved_resolution", "")
        quality = result.get("quality_score", "good")

        update: dict = {
            "reflection_feedback": reflection_feedback,
            "routing_path": routing_path,
        }

        if quality == "needs_improvement" and improved:
            if state.get("escalation_required"):
                update["escalation_notes"] = improved
            else:
                update["resolution"] = improved

        return update

    except Exception as e:
        print(f"[AGENT] reflection_agent error: {e}")
        return {
            "reflection_feedback": f"Reflection skipped due to error: {e}",
            "routing_path": routing_path,
        }
