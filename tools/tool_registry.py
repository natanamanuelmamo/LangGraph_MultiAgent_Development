"""
Tool registry — central registry of all available LangChain tools.

Agents import from here to get access to tools for dynamic selection.
"""

from tools.knowledge_base import search_knowledge_base
from tools.customer_lookup import lookup_customer
from tools.subscription_lookup import lookup_subscription
from tools.ticket_history import get_ticket_history

# All tools available for dynamic selection
ALL_TOOLS = [
    search_knowledge_base,
    lookup_customer,
    lookup_subscription,
    get_ticket_history,
]

# Tool subsets by use case — agents can bind only what's relevant
BILLING_TOOLS = [lookup_subscription, search_knowledge_base, get_ticket_history]
TECHNICAL_TOOLS = [search_knowledge_base, get_ticket_history, lookup_customer]
ACCOUNT_TOOLS = [lookup_customer, search_knowledge_base, get_ticket_history]
GENERAL_TOOLS = [search_knowledge_base, lookup_customer]
TRIAGE_TOOLS = [lookup_customer, get_ticket_history]
