"""
Mock knowledge base search tool.

Matches query keywords against a hardcoded dictionary of support topics
and returns relevant articles with a confidence score.
"""

from langchain_core.tools import tool


# ── Hardcoded Knowledge Base ─────────────────────────────────────────
KNOWLEDGE_BASE: dict[str, list[str]] = {
    "billing": [
        "Billing charges are processed on the 1st of each month.",
        "To dispute a charge, contact support with your transaction ID.",
        "Refunds are typically processed within 5-7 business days.",
    ],
    "refund": [
        "Refunds can be initiated through Settings > Billing > Request Refund.",
        "Duplicate charges are automatically flagged and refunded within 48 hours.",
        "Partial refunds are available for mid-cycle cancellations.",
    ],
    "crash": [
        "If the app crashes on startup, clear cache and data, then reinstall.",
        "Known crash issue on Android 14 — patch v3.2.1 resolves this.",
        "Persistent crashes may indicate a corrupted local database; export data and reinstall.",
    ],
    "export": [
        "Reports can be exported to PDF via Dashboard > Reports > Export.",
        "Excel export is available on Pro and Enterprise plans.",
        "Scheduled exports can be configured under Settings > Automation.",
    ],
    "upgrade": [
        "Plan upgrades take effect immediately; you'll be billed the prorated difference.",
        "Compare plans at Settings > Subscription > View Plans.",
        "Enterprise upgrades require contacting the sales team.",
    ],
    "password": [
        "Reset your password via the login page > 'Forgot Password'.",
        "Passwords must be at least 12 characters with a mix of letters, numbers, and symbols.",
        "If you cannot reset your password, contact support for manual identity verification.",
    ],
    "subscription": [
        "Manage your subscription at Settings > Subscription.",
        "Downgrading a plan takes effect at the end of the current billing cycle.",
        "Annual subscriptions receive a 20% discount compared to monthly billing.",
    ],
    "two-factor": [
        "Enable 2FA at Settings > Security > Two-Factor Authentication.",
        "Supported methods: authenticator app (recommended), SMS, email.",
        "If locked out of 2FA, contact support with your recovery code.",
    ],
    "performance": [
        "Slow dashboard loads may be caused by large datasets — try filtering by date range.",
        "Enable hardware acceleration in Settings > Advanced for better performance.",
        "Clear browser cache if the web app feels sluggish.",
    ],
    "cancel": [
        "Cancel your subscription at Settings > Subscription > Cancel Plan.",
        "Cancellation takes effect at the end of the current billing period.",
        "Data is retained for 30 days after cancellation; download an export before that.",
    ],
}


@tool
def search_knowledge_base(query: str) -> dict:
    """Search the knowledge base for articles matching the query keywords.

    Args:
        query: A natural-language search string.

    Returns:
        dict with keys: found (bool), results (list[str]), confidence (float).
    """
    query_lower = query.lower()
    matched_articles: list[str] = []

    for topic, articles in KNOWLEDGE_BASE.items():
        if topic in query_lower:
            matched_articles.extend(articles)

    if matched_articles:
        # Confidence scales with number of matched topics (capped at 1.0)
        confidence = min(1.0, 0.5 + 0.1 * len(matched_articles))
        return {
            "found": True,
            "results": matched_articles,
            "confidence": confidence,
        }

    return {
        "found": False,
        "results": ["No matching articles found. Consider escalating to a human agent."],
        "confidence": 0.0,
    }
