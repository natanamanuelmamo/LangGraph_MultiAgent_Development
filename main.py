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
from hitl.human_review import display_review_prompt, get_human_decision, handle_human_decision
from scenarios.test_scenarios import (
    SCENARIOS,
    print_result,
)
from dashboard.analytics import print_analytics


def run_ticket_with_hitl(app, ticket_id: str, customer_id: str, message: str) -> dict:
    """
    Run a ticket through the graph with Human-in-the-Loop support.

    Uses the correct LangGraph two-phase resume pattern:
    Phase 1: Run until interrupt (before escalation_agent)
    Phase 2: Update state via graph.update_state(), then resume with None input
    """
    from datetime import datetime, timezone

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

    # ── PHASE 1: Run graph until interrupt ───────────────────────────
    # Graph stops automatically before escalation_agent when
    # escalation_required == True (due to interrupt_before setting)
    state_after_phase1 = app.invoke(initial_state, config=config)

    # ── Check if graph was interrupted ──────────────────────────────
    # Get the current graph state to check if we're at an interrupt
    current_graph_state = app.get_state(config)
    interrupted = bool(current_graph_state.next)  # next is non-empty if interrupted

    if interrupted and state_after_phase1.get("escalation_required", False):
        # Show the human reviewer the ticket details
        display_review_prompt(state_after_phase1)

        # Get human decision
        decision = get_human_decision()

        # Get the state update based on decision
        state_update = handle_human_decision(decision, state_after_phase1)

        # ── PHASE 2: Update checkpoint state then resume ─────────────
        # This is the correct LangGraph resume pattern:
        # 1. Update the persisted state with our changes
        # 2. Resume by calling invoke with None (resumes from checkpoint)
        app.update_state(config, state_update)

        # Resume from checkpoint — None input means "continue from where we stopped"
        final_state = app.invoke(None, config=config)
    else:
        # No escalation needed — graph already completed
        final_state = state_after_phase1

    return final_state


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
        print("\n[MAIN] Running all 5 test scenarios with Human-in-the-Loop...\n")
        results = []
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"\n{'#' * 70}")
            print(f"# RUNNING SCENARIO {i}/{len(SCENARIOS)}: {scenario['description']}")
            print(f"{'#' * 70}")
            try:
                final_state = run_ticket_with_hitl(
                    app,
                    scenario["ticket_id"],
                    scenario["customer_id"],
                    scenario["message"],
                )
                print_result(scenario, final_state)
                results.append(final_state)
            except Exception as e:
                print(f"\n[ERROR] Scenario {i} failed: {e}")
                import traceback
                traceback.print_exc()
                results.append({"ticket_id": scenario["ticket_id"], "error": str(e)})
        print_analytics(results)
    else:
        scenario = SCENARIOS[0]
        print(f"\n[MAIN] Running demo ticket: {scenario['description']}")
        print(f"[MAIN] HITL is active — you will be prompted to approve/reject escalations\n")
        final_state = run_ticket_with_hitl(
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
