"""
LLM helper utility.

Resolves which LLM to use (xAI Grok or OpenAI GPT-4o-mini) based on
environment variables, and provides a smart fallback simulator for local
testing without active API keys.
"""

import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def is_valid_key(key_name: str) -> bool:
    """Check if an environment variable key is present and not a placeholder."""
    val = os.getenv(key_name)
    if not val:
        return False
    val_lower = val.lower()
    return "your_" not in val_lower and val_lower != ""


def get_llm() -> ChatOpenAI | None:
    """Return the resolved ChatOpenAI LLM client, or None if no valid key exists."""
    # Prioritize xAI (Grok) as requested in Tech Stack
    if is_valid_key("XAI_API_KEY"):
        return ChatOpenAI(
            model="grok-2-1212",  # Standard Grok model or grok-3-mini-fast
            temperature=0,
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
    # Fallback to OpenAI GPT-4o-mini as requested in Rules
    elif is_valid_key("OPENAI_API_KEY"):
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    return None


def parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (e.g. ```json or ```)
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


# ── Smart Scenario Fallback Simulator ─────────────────────────────────

def get_simulated_response(agent_name: str, state: dict) -> str:
    """Return high-quality, category-appropriate mock responses for testing

    when no API keys are present or LLM calls fail.
    """
    ticket_id = state.get("ticket_id", "")
    message = state.get("message", "").lower()

    if agent_name == "triage_agent":
        # Match by keywords or ticket ID
        if "charge" in message or "billing" in message or "refund" in message or ticket_id == "T-1001":
            return json.dumps({
                "category": "Billing",
                "priority": "medium",
                "confidence_score": 0.95,
                "reasoning": "Ticket concerns double charges and refund requests."
            })
        elif "crash" in message or "reinstall" in message or ticket_id == "T-1002":
            return json.dumps({
                "category": "Technical Issue",
                "priority": "high",
                "confidence_score": 0.98,
                "reasoning": "Customer reports frequent app crashes causing business disruption."
            })
        elif "dark mode" in message or "feature" in message or ticket_id == "T-1003":
            return json.dumps({
                "category": "Feature Request",
                "priority": "low",
                "confidence_score": 0.92,
                "reasoning": "Requesting user interface dark mode customization."
            })
        elif "export" in message or "how to" in message or ticket_id == "T-1004":
            return json.dumps({
                "category": "General Inquiry",
                "priority": "low",
                "confidence_score": 0.90,
                "reasoning": "General question regarding data exporting functionality."
            })
        elif "hack" in message or "compromised" in message or "password was changed" in message or ticket_id == "T-1005":
            return json.dumps({
                "category": "Account Management",
                "priority": "critical",
                "confidence_score": 0.99,
                "reasoning": "High-severity request indicating compromised account credentials."
            })
        else:
            return json.dumps({
                "category": "General Inquiry",
                "priority": "low",
                "confidence_score": 0.85,
                "reasoning": "Defaulting to general inquiry classification."
            })

    elif agent_name == "billing_agent":
        return json.dumps({
            "agent_notes": "Customer is on the Pro plan and was double charged. Verified last payment status.",
            "resolution": "I have verified your account and can confirm a duplicate charge of $49.99 was processed. I have initiated a full refund for the second transaction. The funds should return to your Visa ending in 4242 within 5-7 business days.",
            "escalation_required": False,
            "escalation_reason": ""
        })

    elif agent_name == "technical_agent":
        # T-1002 has high business impact, so we escalate
        escalate = "losing business" in message or ticket_id == "T-1002"
        return json.dumps({
            "agent_notes": "Frequent crashes reported on startup. Reinstallation didn't resolve it. High business impact.",
            "resolution": "We are sorry for the inconvenience. Let's try clearing the local app cache, or check if you are on Android 14.",
            "escalation_required": escalate,
            "escalation_reason": "Severe business impact due to persistent app crashes." if escalate else ""
        })

    elif agent_name == "feature_request_agent":
        return json.dumps({
            "agent_notes": "Feature request for Dashboard Dark Mode logged.",
            "resolution": "Thank you for the suggestion! We've added dark mode to our product roadmap. It is currently scheduled for development in Q3."
        })

    elif agent_name == "general_inquiry_agent":
        return json.dumps({
            "agent_notes": "Answering question about report export.",
            "resolution": "You can export your monthly reports to PDF or Excel by going to Dashboard > Reports > Export, and selecting your preferred format.",
            "escalation_required": False,
            "escalation_reason": ""
        })

    elif agent_name == "account_agent":
        # Compomised account / hack -> always escalate
        escalate = "hack" in message or "logins" in message or ticket_id == "T-1005"
        return json.dumps({
            "agent_notes": "Suspected account takeover. Logins from foreign locations reported.",
            "resolution": "We detected suspicious activities and will immediately secure your account.",
            "escalation_required": escalate,
            "escalation_reason": "Suspicious logins and password changed without authorization." if escalate else ""
        })

    elif agent_name == "escalation_agent":
        reason = state.get("escalation_reason", "Requires manual intervention.")
        return json.dumps({
            "escalation_notes": f"--- ESCALATION TICKET ---\nTicket: {ticket_id}\nPriority: {state.get('priority', 'critical')}\nCustomer ID: {state.get('customer_id')}\nIssue: {state.get('message')}\nReason: {reason}\nSuggested Next Steps: Lock account temporarily, verify identity, and contact customer directly.",
            "escalation_reason": reason
        })

    elif agent_name == "reflection_agent":
        res = state.get("resolution", "")
        esc = state.get("escalation_notes", "")
        text = esc if state.get("escalation_required") else res
        return json.dumps({
            "reflection_feedback": "The response is clear, professional, and directly addresses the client's concern.",
            "improved_resolution": text,
            "quality_score": "good"
        })

    elif agent_name == "final_response_agent":
        escalated = state.get("escalation_required", False)
        if escalated:
            return json.dumps({
                "final_response": f"Hi {state.get('customer_info', {}).get('name', 'Valued Customer')},\n\nThank you for contacting support (Ticket ID: {ticket_id}). We take your concern very seriously. Your ticket has been escalated to our senior team because of its high priority. A representative will contact you directly at your email address within the next 24 hours.\n\nBest regards,\nCustomer Support Team"
            })
        else:
            return json.dumps({
                "final_response": f"Hi {state.get('customer_info', {}).get('name', 'Valued Customer')},\n\nRegarding Ticket ID: {ticket_id}:\n{state.get('resolution')}\n\nWe hope this resolves your issue. If you have any further questions, please let us know!\n\nBest regards,\nCustomer Support Team"
            })

    return "{}"


def invoke_llm_with_fallback(agent_name: str, prompt: str, state: dict) -> dict:
    """Try to call the real LLM, falling back to the scenario simulator on failure."""
    llm = get_llm()
    if llm is not None:
        try:
            response = llm.invoke(prompt)
            return parse_json(response.content)
        except Exception as e:
            print(f"[LLM HELPER] LLM call failed for {agent_name}: {e}. Falling back to simulation.")
    
    # Fallback simulation
    sim_content = get_simulated_response(agent_name, state)
    return parse_json(sim_content)
