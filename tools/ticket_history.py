"""
Mock ticket history tool.

Returns a list of past support tickets for a given customer.
"""

from langchain_core.tools import tool


# ── Hardcoded Ticket History ─────────────────────────────────────────
TICKET_HISTORY: dict[str, list[dict]] = {
    "C-500": [
        {
            "ticket_id": "T-0801",
            "date": "2025-12-10",
            "category": "Billing",
            "issue": "Incorrect invoice amount",
            "resolution": "Invoice corrected and credit applied",
            "status": "resolved",
        },
        {
            "ticket_id": "T-0802",
            "date": "2026-02-18",
            "category": "General Inquiry",
            "issue": "How to generate monthly reports",
            "resolution": "Provided step-by-step guide",
            "status": "resolved",
        },
        {
            "ticket_id": "T-0803",
            "date": "2026-04-05",
            "category": "Technical Issue",
            "issue": "Dashboard loading slowly",
            "resolution": "Recommended clearing browser cache; performance improved",
            "status": "resolved",
        },
    ],
    "C-501": [
        {
            "ticket_id": "T-0901",
            "date": "2025-11-20",
            "category": "Account Management",
            "issue": "Requested additional user seats",
            "resolution": "Added 5 seats to Enterprise plan",
            "status": "resolved",
        },
        {
            "ticket_id": "T-0902",
            "date": "2026-01-15",
            "category": "Technical Issue",
            "issue": "API rate-limit errors during peak hours",
            "resolution": "Rate limit increased for Enterprise tier",
            "status": "resolved",
        },
    ],
    "C-502": [
        {
            "ticket_id": "T-0701",
            "date": "2026-03-01",
            "category": "Feature Request",
            "issue": "Requested calendar integration",
            "resolution": "Feature noted; added to product roadmap",
            "status": "resolved",
        },
        {
            "ticket_id": "T-0702",
            "date": "2026-05-12",
            "category": "Billing",
            "issue": "Question about upgrade pricing",
            "resolution": "Provided plan comparison and pricing details",
            "status": "resolved",
        },
    ],
}


@tool
def get_ticket_history(customer_id: str) -> list:
    """Retrieve past support tickets for a customer.

    Args:
        customer_id: The unique customer identifier (e.g. "C-500").

    Returns:
        list of dicts, each with: ticket_id, date, category, issue, resolution, status.
    """
    return TICKET_HISTORY.get(customer_id, [])
