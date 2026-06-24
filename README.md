# Customer Support Escalation System

A production-ready multi-agent customer support pipeline built with **LangGraph**, **LangChain**, and **Grok (xAI)** that routes tickets through specialized AI agents, escalates when necessary, and persists state via SQLite.

---

## 📋 Project Overview

This system accepts a customer support ticket and processes it through a directed graph of specialized AI agents:

1. **Triage** — classifies the ticket by category, priority, and confidence  
2. **Specialist** — a domain-specific agent handles the issue  
3. **Escalation** *(conditional)* — generates a detailed hand-off summary when needed  
4. **Reflection** *(bonus)* — QA-reviews and improves the response  
5. **Final Response** — produces the polished customer-facing message  

Every step is checkpointed to SQLite so tickets can be paused and resumed.

---

## 🏗️ System Architecture

```
                         ┌──────────────┐
                         │  START       │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │ triage_agent │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │ (conditional routing by category)  │
     ┌────────▼──┐  ┌────▼────┐  ┌──▼──────┐  ┌───▼─────┐  ┌───▼──────┐
     │ billing   │  │technical│  │feature  │  │general  │  │account   │
     │ _agent    │  │ _agent  │  │_request │  │_inquiry │  │ _agent   │
     └────┬──────┘  └────┬────┘  │ _agent  │  │ _agent  │  └────┬─────┘
          │              │       └────┬────┘  └────┬────┘       │
          └──────────────┴────────────┴────────────┴────────────┘
                                      │
                       (conditional: escalation_required?)
                        ┌─────────────┴─────────────┐
                   Yes  │                           │  No
               ┌────────▼─────┐              ┌──────▼──────┐
               │ escalation   │              │ reflection  │
               │ _agent       │              │ _agent      │
               └────────┬─────┘              └──────┬──────┘
                        │                           │
                        └───────► reflection ◄──────┘
                                  _agent
                                    │
                           ┌────────▼────────┐
                           │ final_response  │
                           │ _agent          │
                           └────────┬────────┘
                                    │
                              ┌─────▼─────┐
                              │    END     │
                              └───────────┘
```

---

## 🤖 Agent Responsibilities

| Agent | Responsibility |
|---|---|
| **triage_agent** | Classifies category, priority, confidence; enriches with customer data |
| **billing_agent** | Analyses billing issues (charges, refunds, invoices) |
| **technical_agent** | Diagnoses technical problems (crashes, bugs, performance) |
| **feature_request_agent** | Acknowledges feature requests; never escalates |
| **general_inquiry_agent** | Answers general how-to questions from the KB |
| **account_agent** | Handles account issues; forces escalation on security concerns |
| **escalation_agent** | Writes detailed escalation summary for human agents |
| **reflection_agent** | QA-reviews clarity, tone, completeness; rewrites if needed |
| **final_response_agent** | Generates the polished customer-facing message |

---

## 📦 State Design

| Field | Type | Description |
|---|---|---|
| `ticket_id` | str | Unique ticket identifier |
| `customer_id` | str | Customer identifier |
| `message` | str | Original customer message |
| `category` | str | Classified category (set by triage) |
| `priority` | str | low / medium / high / critical |
| `confidence_score` | float | 0.0–1.0 classification confidence |
| `customer_info` | dict | Customer profile from lookup tool |
| `subscription_info` | dict | Subscription data from lookup tool |
| `ticket_history` | list | Past tickets from history tool |
| `knowledge_base_results` | list | Matched KB articles |
| `agent_notes` | str | Specialist agent analysis notes |
| `resolution` | str | Proposed resolution text |
| `escalation_required` | bool | Whether escalation is needed |
| `escalation_reason` | str | Reason for escalation |
| `escalation_notes` | str | Detailed escalation summary |
| `reflection_feedback` | str | Reflection agent review notes |
| `final_response` | str | Customer-facing response |
| `resolved` | bool | Whether issue was fully resolved |
| `routing_path` | list[str] | Ordered list of agents visited |
| `tools_used` | list[str] | Names of tools called |
| `created_at` | str | ISO creation timestamp |

---

## 🔀 Routing Logic

### After Triage (5-way conditional)
Routes based on `category`:
- `"Billing"` → `billing_agent`
- `"Technical Issue"` → `technical_agent`
- `"Feature Request"` → `feature_request_agent`
- `"General Inquiry"` → `general_inquiry_agent`
- `"Account Management"` → `account_agent`
- *(fallback)* → `general_inquiry_agent`

### After Specialist (2-way conditional)
- `escalation_required == True` → `escalation_agent`
- `escalation_required == False` → `reflection_agent`

### After Reflection / Escalation
- `escalation_agent` → `reflection_agent` (fixed edge)
- `reflection_agent` → `final_response_agent` (fixed edge)
- `final_response_agent` → `END`

---

## 🛠️ Tool Integration

| Tool | Module | Returns |
|---|---|---|
| `search_knowledge_base` | `tools/knowledge_base.py` | `{found, results, confidence}` — keyword match against 10 topics |
| `lookup_customer` | `tools/customer_lookup.py` | `{name, email, plan, member_since, account_status}` |
| `lookup_subscription` | `tools/subscription_lookup.py` | `{plan_name, status, billing_cycle, amount, features, ...}` |
| `get_ticket_history` | `tools/ticket_history.py` | List of past tickets with category, resolution, status |

All tools are **mock implementations** with hardcoded data for 3 customers (C-500, C-501, C-502).

---

## 💾 Persistence Strategy

- **Engine**: SQLite via `langgraph.checkpoint.sqlite.SqliteSaver`
- **File**: `support_system.db` (created automatically)
- **Thread ID**: Each ticket uses its `ticket_id` as the `thread_id`, so every ticket's state is independently persisted and resumable
- **Usage**: Pass `config={"configurable": {"thread_id": ticket_id}}` when invoking the graph

---

## ⚡ How to Install

```bash
# 1. Clone or navigate to the project
cd customer_support_system

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your xAI API key
#    Edit .env and replace the placeholder:
#    XAI_API_KEY=your_actual_key_here
```

---

## ▶️ How to Run

```bash
# Run a single demo ticket (Scenario 1 — Billing)
python main.py

# Run all 5 test scenarios + analytics dashboard
python main.py --all
```

---

## 🧪 Test Scenarios

| # | Ticket | Type | Expected Escalation |
|---|---|---|---|
| 1 | T-1001 | Billing (duplicate charge) | No |
| 2 | T-1002 | Technical (app crash, business impact) | Yes |
| 3 | T-1003 | Feature Request (dark mode) | No |
| 4 | T-1004 | General Inquiry (report export) | No |
| 5 | T-1005 | Account Security (suspected hack) | Yes |

---

## ⭐ Bonus Features

- **Reflection Agent** — QA-reviews every response for clarity, tone, and completeness before it reaches the customer
- **Analytics Dashboard** — after running all scenarios, prints aggregate stats: escalation rate, resolution rate, category/priority breakdowns, tool usage, and routing path metrics
- **Escalation Notifications** — escalation agent prints a simulated email/Telegram notification to the console
- **Human-in-the-Loop (HITL)** — When the specialist agent recommends escalation, the graph automatically pauses before the escalation_agent using LangGraph's interrupt_before feature. The human reviewer sees the full ticket summary, agent notes, and escalation reason, then types 'approve' or 'reject'. If approved, the graph resumes and runs the escalation agent normally. If rejected, escalation_required is set to False and the ticket routes directly to reflection and final response without escalation. This is implemented via interrupt_before=["escalation_agent"] in graph.compile().
- **Multiple Tool Selection** — Three specialist agents (billing_agent, technical_agent, account_agent) now use dynamic tool selection via LangChain's bind_tools() API. Instead of calling tools in a hardcoded sequence, the LLM receives a list of available tools relevant to its domain and autonomously decides which ones to call based on the ticket content. For example, a simple billing question may only trigger search_knowledge_base, while a complex billing issue triggers both lookup_subscription and get_ticket_history. The smart tool caller is implemented in agents/smart_tool_caller.py and the tool registry is in tools/tool_registry.py. Tool selection decisions are logged with [SMART TOOLS] prefix.

---

## 📁 Project Structure

```
customer_support_system/
├── .env / .env.example        Environment variables
├── requirements.txt           Python dependencies
├── README.md                  This file
├── main.py                    CLI entry point
├── graph/
│   ├── state.py               Shared TypedDict state
│   ├── router.py              Conditional routing logic
│   └── graph_builder.py       LangGraph assembly
├── agents/                    9 specialized agents
├── tools/                     4 mock LangChain tools
├── persistence/               SQLite checkpointer
├── scenarios/                 5 test scenarios
└── dashboard/                 Analytics summary
```
