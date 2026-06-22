"""
Shared state definition for the Customer Support Escalation System.

This TypedDict defines the complete state schema that flows through
the LangGraph pipeline. Each agent reads from and writes partial
updates back to this state.
"""

from typing import TypedDict


class SupportTicketState(TypedDict):
    """Full state schema for a customer support ticket flowing through the graph."""

    # ── Ticket Identity ──────────────────────────────────────────────
    ticket_id: str                  # Unique ticket identifier (e.g. "T-1001")
    customer_id: str                # Customer identifier (e.g. "C-500")
    message: str                    # Original customer message

    # ── Classification (set by triage agent) ─────────────────────────
    category: str                   # Billing | Technical Issue | Feature Request | General Inquiry | Account Management
    priority: str                   # low | medium | high | critical
    confidence_score: float         # 0.0 – 1.0 confidence in classification

    # ── Enrichment Data (populated by tools) ─────────────────────────
    customer_info: dict             # From customer_lookup tool
    subscription_info: dict         # From subscription_lookup tool
    ticket_history: list            # From ticket_history tool
    knowledge_base_results: list    # From knowledge_base tool

    # ── Agent Analysis ───────────────────────────────────────────────
    agent_notes: str                # Notes from the specialist agent
    resolution: str                 # Proposed resolution text

    # ── Escalation ───────────────────────────────────────────────────
    escalation_required: bool       # Whether to escalate to human
    escalation_reason: str          # Why escalation is needed
    escalation_notes: str           # Detailed summary for human agent

    # ── Reflection (BONUS) ───────────────────────────────────────────
    reflection_feedback: str        # Feedback from the reflection agent

    # ── Final Output ─────────────────────────────────────────────────
    final_response: str             # Customer-facing response message
    resolved: bool                  # Whether the issue was fully resolved

    # ── Observability ────────────────────────────────────────────────
    routing_path: list[str]         # Ordered list of agents visited
    tools_used: list[str]           # Names of tools called during processing
    created_at: str                 # ISO timestamp of ticket creation
