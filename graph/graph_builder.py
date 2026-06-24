"""
LangGraph graph assembly for the Customer Support Escalation System.

Builds a StateGraph with 9 nodes, conditional routing after triage
and after each specialist, and SQLite persistence.
"""

from langgraph.graph import StateGraph, END

from graph.state import SupportTicketState
from graph.router import route_after_triage, route_after_specialist

from agents.triage_agent import triage_agent
from agents.billing_agent import billing_agent
from agents.technical_agent import technical_agent
from agents.feature_request_agent import feature_request_agent
from agents.general_inquiry_agent import general_inquiry_agent
from agents.account_agent import account_agent
from agents.escalation_agent import escalation_agent
from agents.reflection_agent import reflection_agent
from agents.final_response_agent import final_response_agent

from persistence.checkpointer import get_checkpointer


def build_graph():
    """Assemble and compile the full support pipeline graph.

    Returns:
        A compiled LangGraph application with SQLite checkpointing.
    """
    graph = StateGraph(SupportTicketState)

    # ── 1. Add all 9 nodes ───────────────────────────────────────────
    graph.add_node("triage_agent", triage_agent)
    graph.add_node("billing_agent", billing_agent)
    graph.add_node("technical_agent", technical_agent)
    graph.add_node("feature_request_agent", feature_request_agent)
    graph.add_node("general_inquiry_agent", general_inquiry_agent)
    graph.add_node("account_agent", account_agent)
    graph.add_node("escalation_agent", escalation_agent)
    graph.add_node("reflection_agent", reflection_agent)
    graph.add_node("final_response_agent", final_response_agent)

    # ── 2. Entry point ───────────────────────────────────────────────
    graph.set_entry_point("triage_agent")

    # ── 3. Conditional edge: triage → specialist ─────────────────────
    graph.add_conditional_edges(
        "triage_agent",
        route_after_triage,
        {
            "billing_agent": "billing_agent",
            "technical_agent": "technical_agent",
            "feature_request_agent": "feature_request_agent",
            "general_inquiry_agent": "general_inquiry_agent",
            "account_agent": "account_agent",
        },
    )

    # ── 4. Conditional edge: each specialist → escalation | reflection
    specialist_nodes = [
        "billing_agent",
        "technical_agent",
        "feature_request_agent",
        "general_inquiry_agent",
        "account_agent",
    ]
    for node in specialist_nodes:
        graph.add_conditional_edges(
            node,
            route_after_specialist,
            {
                "escalation_agent": "escalation_agent",
                "reflection_agent": "reflection_agent",
            },
        )

    # ── 5. Fixed edges ───────────────────────────────────────────────
    graph.add_edge("escalation_agent", "reflection_agent")
    graph.add_edge("reflection_agent", "final_response_agent")
    graph.add_edge("final_response_agent", END)

    # ── 6. Compile with persistence ──────────────────────────────────
    checkpointer = get_checkpointer()
    app = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["escalation_agent"],
    )
    return app
