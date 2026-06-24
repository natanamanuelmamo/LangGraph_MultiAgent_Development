"""
Human-in-the-Loop review handler.

When the graph is interrupted before escalation_agent, this module
handles pausing, displaying ticket info to the human reviewer, 
collecting their decision, and resuming the graph.
"""

def display_review_prompt(state: dict) -> None:
    """Print the ticket summary for the human reviewer to evaluate."""
    print("\n" + "=" * 70)
    print("  *** HUMAN REVIEW REQUIRED ***")
    print("=" * 70)
    print(f"  Ticket ID     : {state.get('ticket_id', 'N/A')}")
    print(f"  Customer      : {state.get('customer_info', {}).get('name', 'Unknown')}")
    print(f"  Category      : {state.get('category', 'N/A')}")
    print(f"  Priority      : {state.get('priority', 'N/A')}")
    print(f"  Confidence    : {state.get('confidence_score', 0.0):.2f}")
    print(f"  Message       : {state.get('message', 'N/A')}")
    print(f"  Agent Notes   : {state.get('agent_notes', 'N/A')}")
    print(f"  Esc. Reason   : {state.get('escalation_reason', 'N/A')}")
    print("-" * 70)
    print("  The specialist agent recommends ESCALATING this ticket.")
    print("  Please review the above information and decide.")
    print("=" * 70)


def get_human_decision() -> str:
    """Prompt the human reviewer for approve/reject input."""
    while True:
        decision = input("\n  Approve escalation? Type 'approve' or 'reject': ").strip().lower()
        if decision in ("approve", "reject"):
            return decision
        print("  Invalid input. Please type exactly 'approve' or 'reject'.")


def handle_human_decision(decision: str, state: dict) -> dict:
    """
    Update state based on the human's decision.
    
    - approve: keep escalation_required=True, graph continues to escalation_agent
    - reject:  set escalation_required=False, graph skips to reflection_agent
    """
    if decision == "approve":
        print("\n  [HITL] Escalation APPROVED by human reviewer.")
        print("  [HITL] Proceeding to escalation agent...\n")
        return {"escalation_required": True}
    else:
        print("\n  [HITL] Escalation REJECTED by human reviewer.")
        print("  [HITL] Routing directly to reflection agent...\n")
        return {
            "escalation_required": False,
            "escalation_reason": "",
            "escalation_notes": "Escalation rejected by human reviewer.",
        }
