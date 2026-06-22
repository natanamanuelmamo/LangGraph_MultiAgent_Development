"""
Mock subscription lookup tool.

Returns synthetic subscription/billing data based on customer ID.
"""

from langchain_core.tools import tool


# ── Hardcoded Subscription Database ──────────────────────────────────
SUBSCRIPTIONS: dict[str, dict] = {
    "C-500": {
        "plan_name": "Pro",
        "status": "active",
        "billing_cycle": "monthly",
        "next_billing_date": "2026-07-01",
        "amount": 49.99,
        "features": ["Advanced Analytics", "Priority Support", "API Access", "PDF Export"],
        "payment_method": "Visa ending in 4242",
        "last_payment_status": "success",
    },
    "C-501": {
        "plan_name": "Enterprise",
        "status": "active",
        "billing_cycle": "annual",
        "next_billing_date": "2027-08-01",
        "amount": 499.99,
        "features": [
            "Advanced Analytics", "Priority Support", "API Access",
            "PDF Export", "Custom Integrations", "Dedicated Account Manager",
            "SSO", "Audit Logs",
        ],
        "payment_method": "Corporate Invoice",
        "last_payment_status": "success",
    },
    "C-502": {
        "plan_name": "Basic",
        "status": "active",
        "billing_cycle": "monthly",
        "next_billing_date": "2026-07-10",
        "amount": 9.99,
        "features": ["Basic Analytics", "Email Support"],
        "payment_method": "Mastercard ending in 8888",
        "last_payment_status": "success",
    },
}

DEFAULT_SUBSCRIPTION: dict = {
    "plan_name": "Basic",
    "status": "active",
    "billing_cycle": "monthly",
    "next_billing_date": "2026-07-01",
    "amount": 9.99,
    "features": ["Basic Analytics", "Email Support"],
    "payment_method": "Unknown",
    "last_payment_status": "unknown",
}


@tool
def lookup_subscription(customer_id: str) -> dict:
    """Look up subscription and billing information for a customer.

    Args:
        customer_id: The unique customer identifier (e.g. "C-500").

    Returns:
        dict with keys: plan_name, status, billing_cycle, next_billing_date,
        amount, features, payment_method, last_payment_status.
    """
    subscription = SUBSCRIPTIONS.get(customer_id, DEFAULT_SUBSCRIPTION).copy()
    subscription["customer_id"] = customer_id
    return subscription
