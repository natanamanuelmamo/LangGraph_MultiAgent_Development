"""
Mock customer lookup tool.

Returns synthetic customer profile data based on a customer ID.
"""

from langchain_core.tools import tool


# ── Hardcoded Customer Database ──────────────────────────────────────
CUSTOMERS: dict[str, dict] = {
    "C-500": {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "plan": "Pro",
        "member_since": "2023-03-15",
        "account_status": "active",
    },
    "C-501": {
        "name": "Bob Williams",
        "email": "bob.williams@example.com",
        "plan": "Enterprise",
        "member_since": "2022-08-01",
        "account_status": "active",
    },
    "C-502": {
        "name": "Carol Martinez",
        "email": "carol.martinez@example.com",
        "plan": "Basic",
        "member_since": "2024-01-10",
        "account_status": "active",
    },
}

DEFAULT_CUSTOMER: dict = {
    "name": "Unknown Customer",
    "email": "unknown@example.com",
    "plan": "Basic",
    "member_since": "2024-01-01",
    "account_status": "active",
}


@tool
def lookup_customer(customer_id: str) -> dict:
    """Look up customer profile information by customer ID.

    Args:
        customer_id: The unique customer identifier (e.g. "C-500").

    Returns:
        dict with keys: name, email, plan, member_since, account_status.
    """
    customer = CUSTOMERS.get(customer_id, DEFAULT_CUSTOMER).copy()
    customer["customer_id"] = customer_id
    return customer
