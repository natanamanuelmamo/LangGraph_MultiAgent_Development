"""
Conditional routing logic for the LangGraph support pipeline.

These functions are used as conditional edge selectors to determine
which node the graph should visit next.
"""


def route_after_triage(state: dict) -> str:
    """Route to the appropriate specialist agent based on ticket category."""
    category = state.get("category", "")
    mapping = {
        "Billing": "billing_agent",
        "Technical Issue": "technical_agent",
        "Feature Request": "feature_request_agent",
        "General Inquiry": "general_inquiry_agent",
        "Account Management": "account_agent",
    }
    destination = mapping.get(category, "general_inquiry_agent")
    print(f"[ROUTER] Routing ticket category '{category}' -> {destination}")
    return destination


def route_after_specialist(state: dict) -> str:
    """Route to escalation or reflection based on escalation_required flag."""
    if state.get("escalation_required", False):
        print("[ROUTER] Escalation required -> escalation_agent")
        return "escalation_agent"
    print("[ROUTER] No escalation -> reflection_agent")
    return "reflection_agent"


def route_after_reflection(state: dict) -> str:
    """Always proceed to the final response agent after reflection."""
    return "final_response_agent"
