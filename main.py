"""
Customer Support Escalation System — CLI Entry Point.

Usage:
    python main.py                Run a single demo ticket
    python main.py --all          Run all 5 test scenarios + analytics
"""

import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from graph.graph_builder import build_graph
from scenarios.test_scenarios import (
    SCENARIOS,
    build_initial_state,
    print_result,
    run_all_scenarios,
)
from dashboard.analytics import print_analytics


def run_single_ticket(app, ticket_id: str, customer_id: str, message: str) -> dict:
    """Run a single ticket through the support pipeline."""
    initial_state = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "message": message,
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

    config = {"configurable": {"thread_id": ticket_id}}
    final_state = app.invoke(initial_state, config=config)
    return final_state


def main():
    print("=" * 70)
    print("  CUSTOMER SUPPORT ESCALATION SYSTEM")
    print("  Powered by LangGraph + Groq (llama-3.3-70b-versatile)")
    print("=" * 70)

    app = build_graph()

    if "--all" in sys.argv:
        # ── Run all 5 test scenarios ─────────────────────────────────
        print("\n[MAIN] Running all 5 test scenarios...\n")
        results = run_all_scenarios(app)
        print_analytics(results)
    else:
        # ── Run a single demo ticket ────────────────────────────────
        scenario = SCENARIOS[0]  # Default to first scenario
        print(f"\n[MAIN] Running demo ticket: {scenario['description']}")
        print(f"[MAIN] Use --all flag to run all 5 scenarios\n")

        final_state = run_single_ticket(
            app,
            scenario["ticket_id"],
            scenario["customer_id"],
            scenario["message"],
        )

        demo_scenario = {"description": scenario["description"]}
        print_result(demo_scenario, final_state)
        print_analytics([final_state])


if __name__ == "__main__":
    main()
