"""
Test scenarios for the Customer Support Escalation System.

Defines 5 representative tickets and provides a runner function
that executes them through the compiled graph.
"""

from datetime import datetime, timezone


# ── Scenario Definitions ─────────────────────────────────────────────

SCENARIOS = [
    {
        "ticket_id": "T-1001",
        "customer_id": "C-500",
        "message": (
            "I was charged twice for my subscription this month. "
            "Please refund the duplicate charge immediately."
        ),
        "description": "Billing Issue - duplicate charge / refund request",
        "expected_path": "triage -> billing_agent -> reflection -> final_response",
        "expected_escalation": False,
    },
    {
        "ticket_id": "T-1002",
        "customer_id": "C-501",
        "message": (
            "The mobile app crashes every time I try to open it. "
            "I've tried reinstalling but nothing works. "
            "I'm losing business because of this."
        ),
        "description": "Technical Issue - app crash with business impact",
        "expected_path": "triage -> technical_agent -> escalation -> reflection -> final_response",
        "expected_escalation": True,
    },
    {
        "ticket_id": "T-1003",
        "customer_id": "C-502",
        "message": (
            "I would love to have a dark mode option in the dashboard. "
            "Can you add this feature?"
        ),
        "description": "Feature Request - dark mode",
        "expected_path": "triage -> feature_request_agent -> reflection -> final_response",
        "expected_escalation": False,
    },
    {
        "ticket_id": "T-1004",
        "customer_id": "C-500",
        "message": "How do I export my monthly reports to PDF or Excel?",
        "description": "General Inquiry - report export how-to",
        "expected_path": "triage -> general_inquiry_agent -> reflection -> final_response",
        "expected_escalation": False,
    },
    {
        "ticket_id": "T-1005",
        "customer_id": "C-501",
        "message": (
            "I think someone hacked my account. "
            "I see logins from countries I've never been to "
            "and my password was changed without my knowledge."
        ),
        "description": "Account Security - suspected breach (escalated)",
        "expected_path": "triage -> account_agent -> escalation -> reflection -> final_response",
        "expected_escalation": True,
    },
]


def build_initial_state(scenario: dict) -> dict:
    """Convert a scenario dict into a valid initial SupportTicketState."""
    return {
        "ticket_id": scenario["ticket_id"],
        "customer_id": scenario["customer_id"],
        "message": scenario["message"],
        "category": "",
        "priority": "",
        "confidence_score": 0.0,
        "customer_info": {},
        "subscription_info": {},
        "ticket_history": [],
        "knowledge_base_results": [],
        "agent_notes": "",
        "resolution": "",
        "escalation_required": False,
        "escalation_reason": "",
        "escalation_notes": "",
        "reflection_feedback": "",
        "final_response": "",
        "routing_path": [],
        "tools_used": [],
        "resolved": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def print_result(scenario: dict, final_state: dict) -> None:
    """Print a formatted summary of a completed scenario."""
    print("\n" + "=" * 70)
    print(f"  SCENARIO: {scenario['description']}")
    print("=" * 70)
    print(f"  Ticket ID    : {final_state.get('ticket_id', 'N/A')}")
    print(f"  Customer ID  : {final_state.get('customer_id', 'N/A')}")
    ci = final_state.get("customer_info", {})
    print(f"  Customer     : {ci.get('name', 'Unknown')} ({ci.get('plan', 'N/A')} plan)")
    print(f"  Category     : {final_state.get('category', 'N/A')}")
    print(f"  Priority     : {final_state.get('priority', 'N/A')}")
    print(f"  Confidence   : {final_state.get('confidence_score', 0.0):.2f}")
    print(f"  Routing Path : {' -> '.join(final_state.get('routing_path', []))}")
    print(f"  Tools Used   : {', '.join(final_state.get('tools_used', []))}")

    escalated = final_state.get("escalation_required", False)
    print(f"  Escalated?   : {'Yes' if escalated else 'No'}")
    if escalated:
        print(f"  Esc. Reason  : {final_state.get('escalation_reason', 'N/A')}")

    print(f"  Resolved?    : {'Yes' if final_state.get('resolved', False) else 'No'}")
    print("-" * 70)
    print("  FINAL RESPONSE:")
    print("-" * 70)
    for line in final_state.get("final_response", "N/A").split("\n"):
        print(f"  {line}")
    print("=" * 70)


def run_all_scenarios(app) -> list[dict]:
    """Execute all 5 test scenarios and return the list of final states."""
    results = []

    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\n{'#' * 70}")
        print(f"# RUNNING SCENARIO {i}/{len(SCENARIOS)}: {scenario['description']}")
        print(f"{'#' * 70}")

        initial_state = build_initial_state(scenario)
        config = {"configurable": {"thread_id": scenario["ticket_id"]}}

        try:
            final_state = app.invoke(initial_state, config=config)
            print_result(scenario, final_state)
            results.append(final_state)
        except Exception as e:
            print(f"\n[ERROR] Scenario {i} failed: {e}")
            results.append({"ticket_id": scenario["ticket_id"], "error": str(e)})

    return results
