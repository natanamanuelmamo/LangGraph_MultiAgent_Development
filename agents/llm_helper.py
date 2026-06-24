"""
LLM helper utility.

Resolves which LLM to use based on available environment variables:
  1. Groq (primary) — fast, free, no credit card required
  2. OpenAI GPT-4o-mini (fallback) — if Groq key not present
  3. Smart scenario simulator — if no API keys present at all

Get a free Groq API key at: https://console.groq.com
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()


def is_valid_key(key_name: str) -> bool:
    """Check if an environment variable key is present and not a placeholder."""
    val = os.getenv(key_name)
    if not val:
        return False
    val_lower = val.lower()
    return "your_" not in val_lower and val_lower != ""


def get_llm():
    """Return the resolved LLM client, or None if no valid key exists.
    
    Priority order:
    1. Groq (llama-3.3-70b-versatile) — free tier, fast, no credit card
    2. OpenAI (gpt-4o-mini) — fallback if Groq key not present
    """
    # Priority 1: Groq
    if is_valid_key("GROQ_API_KEY"):
        from langchain_groq import ChatGroq
        print("[LLM HELPER] Using Groq (llama-3.3-70b-versatile)")
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    # Priority 2: OpenAI fallback
    if is_valid_key("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        print("[LLM HELPER] Using OpenAI (gpt-4o-mini)")
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
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


# ── Smart Scenario Fallback Simulator ─────────────────────────────────

def get_simulated_response(agent_name: str, state: dict) -> str:
    """Return scenario-appropriate mock responses when no API keys are present."""
    ticket_id = state.get("ticket_id", "")
    message = state.get("message", "").lower()

    if agent_name == "triage_agent":
        if "charge" in message or "billing" in message or "refund" in message or ticket_id == "T-1001":
            return json.dumps({
                "category": "Billing", "priority": "medium",
                "confidence_score": 0.95,
                "reasoning": "Ticket concerns double charges and refund requests."
            })
        elif "crash" in message or "reinstall" in message or ticket_id == "T-1002":
            return json.dumps({
                "category": "Technical Issue", "priority": "high",
                "confidence_score": 0.98,
                "reasoning": "Customer reports frequent app crashes causing business disruption."
            })
        elif "dark mode" in message or "feature" in message or ticket_id == "T-1003":
            return json.dumps({
                "category": "Feature Request", "priority": "low",
                "confidence_score": 0.92,
                "reasoning": "Requesting user interface dark mode customization."
            })
        elif "export" in message or "how to" in message or ticket_id == "T-1004":
            return json.dumps({
                "category": "General Inquiry", "priority": "low",
                "confidence_score": 0.90,
                "reasoning": "General question regarding data exporting functionality."
            })
        elif "hack" in message or "compromised" in message or "password was changed" in message or ticket_id == "T-1005":
            return json.dumps({
                "category": "Account Management", "priority": "critical",
                "confidence_score": 0.99,
                "reasoning": "High-severity request indicating compromised account credentials."
            })
        else:
            return json.dumps({
                "category": "General Inquiry", "priority": "low",
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
        escalate = "losing business" in message or ticket_id == "T-1002"
        return json.dumps({
            "agent_notes": "Frequent crashes reported on startup. Reinstallation did not resolve it. High business impact.",
            "resolution": "We are sorry for the inconvenience. Let us try clearing the local app cache, or check if you are on Android 14.",
            "escalation_required": escalate,
            "escalation_reason": "Severe business impact due to persistent app crashes." if escalate else ""
        })

    elif agent_name == "feature_request_agent":
        return json.dumps({
            "agent_notes": "Feature request for Dashboard Dark Mode logged.",
            "resolution": "Thank you for the suggestion! We have added dark mode to our product roadmap. It is currently scheduled for development in Q3."
        })

    elif agent_name == "general_inquiry_agent":
        return json.dumps({
            "agent_notes": "Answering question about report export.",
            "resolution": "You can export your monthly reports to PDF or Excel by going to Dashboard > Reports > Export, and selecting your preferred format.",
            "escalation_required": False,
            "escalation_reason": ""
        })

    elif agent_name == "account_agent":
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
            "escalation_notes": (
                f"--- ESCALATION TICKET ---\n"
                f"Ticket: {ticket_id}\n"
                f"Priority: {state.get('priority', 'critical')}\n"
                f"Customer ID: {state.get('customer_id')}\n"
                f"Issue: {state.get('message')}\n"
                f"Reason: {reason}\n"
                f"Suggested Next Steps: Lock account temporarily, verify identity, and contact customer directly."
            ),
            "escalation_reason": reason
        })

    elif agent_name == "reflection_agent":
        res = state.get("resolution", "")
        esc = state.get("escalation_notes", "")
        text = esc if state.get("escalation_required") else res
        return json.dumps({
            "reflection_feedback": "The response is clear, professional, and directly addresses the client concern.",
            "improved_resolution": text,
            "quality_score": "good"
        })

    elif agent_name == "final_response_agent":
        escalated = state.get("escalation_required", False)
        name = state.get("customer_info", {}).get("name", "Valued Customer")
        if escalated:
            return json.dumps({
                "final_response": (
                    f"Hi {name},\n\n"
                    f"Thank you for contacting support (Ticket ID: {ticket_id}). "
                    f"We take your concern very seriously. Your ticket has been escalated "
                    f"to our senior team. A representative will contact you within 24 hours.\n\n"
                    f"Best regards,\nCustomer Support Team"
                )
            })
        else:
            return json.dumps({
                "final_response": (
                    f"Hi {name},\n\n"
                    f"Regarding Ticket ID: {ticket_id}:\n"
                    f"{state.get('resolution')}\n\n"
                    f"We hope this resolves your issue. If you have further questions, please let us know!\n\n"
                    f"Best regards,\nCustomer Support Team"
                )
            })

    return "{}"


def invoke_llm_with_fallback(agent_name: str, prompt: str, state: dict) -> dict:
    """Try the real LLM first; fall back to the scenario simulator on failure."""
    llm = get_llm()
    if llm is not None:
        try:
            response = llm.invoke(prompt)
            return parse_json(response.content)
        except Exception as e:
            print(f"[LLM HELPER] LLM call failed for {agent_name}: {e}. Falling back to simulation.")

    # Fallback simulation (no API keys or LLM call failed)
    print(f"[LLM HELPER] Using simulation for {agent_name}")
    sim_content = get_simulated_response(agent_name, state)
    return parse_json(sim_content)
