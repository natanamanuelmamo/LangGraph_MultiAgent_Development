"""
Final Response Agent — generates the customer-facing response.

If resolved: friendly resolution message.
If escalated: empathetic message saying their ticket has been escalated and they will hear back soon.
"""

from agents.llm_helper import invoke_llm_with_fallback


def final_response_agent(state: dict) -> dict:
    """Generate the final customer-facing response."""
    ticket_id = state.get("ticket_id", "UNKNOWN")
    escalated = state.get("escalation_required", False)

    print(f"[AGENT] Running final_response_agent for ticket {ticket_id}")

    routing_path = list(state.get("routing_path", []))
    routing_path.append("final_response_agent")

    customer_name = state.get("customer_info", {}).get("name", "Valued Customer")

    prompt = f"""You are writing the final customer-facing response for a support ticket.

TICKET ID: {ticket_id}
CUSTOMER NAME: {customer_name}
CATEGORY: {state.get("category", "General")}
ORIGINAL MESSAGE: {state.get("message", "")}
RESOLUTION: {state.get("resolution", "")}
ESCALATED: {escalated}
ESCALATION REASON: {state.get("escalation_reason", "")}
REFLECTION FEEDBACK: {state.get("reflection_feedback", "")}

{"This ticket was ESCALATED. Write an empathetic message explaining that their issue has been forwarded to a senior agent and they will hear back within 24 hours." if escalated else "This ticket was RESOLVED. Write a friendly, complete resolution message with clear next steps."}

Include the ticket ID for reference. Be professional, warm, and helpful.

Respond with ONLY valid JSON:
{{
  "final_response": "<complete customer-facing message>"
}}"""

    try:
        result = invoke_llm_with_fallback("final_response_agent", prompt, state)
        final_response = result.get("final_response", "")
    except Exception as e:
        print(f"[AGENT] final_response_agent error: {e}")
        if escalated:
            final_response = (
                f"Dear {customer_name},\n\n"
                f"Thank you for contacting us (Ticket: {ticket_id}). "
                f"Your issue has been escalated to our senior support team. "
                f"You will hear back within 24 hours.\n\n"
                f"Best regards,\nCustomer Support"
            )
        else:
            final_response = (
                f"Dear {customer_name},\n\n"
                f"Thank you for contacting us (Ticket: {ticket_id}). "
                f"{state.get('resolution', 'We have addressed your concern.')}\n\n"
                f"Best regards,\nCustomer Support"
            )

    resolved = not escalated

    return {
        "final_response": final_response,
        "resolved": resolved,
        "routing_path": routing_path,
    }
