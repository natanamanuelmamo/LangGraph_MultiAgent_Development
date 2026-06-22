"""
SQLite checkpointing setup for LangGraph.

Provides a persistent SqliteSaver so that each ticket's graph state
can be independently saved and resumed using the ticket_id as thread_id.
"""

import os
from langgraph.checkpoint.sqlite import SqliteSaver

# Database file lives alongside the project root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "support_system.db")

# Module-level singleton so every import shares the same connection
_checkpointer: SqliteSaver | None = None


def get_checkpointer() -> SqliteSaver:
    """Return (and lazily create) the shared SqliteSaver instance.

    The saver persists graph state to 'support_system.db'.
    Each ticket should be invoked with:
        config = {"configurable": {"thread_id": ticket_id}}
    so that state is partitioned per ticket.
    """
    global _checkpointer
    if _checkpointer is None:
        import sqlite3
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
    return _checkpointer
