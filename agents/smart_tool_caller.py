"""
Smart Tool Caller — enables dynamic tool selection via LLM tool-calling.

This module gives agents the ability to let the LLM decide which tools
to call based on the ticket content, rather than hardcoding sequences.
"""

import json
from agents.llm_helper import get_llm


def run_with_dynamic_tools(
    agent_name: str,
    system_prompt: str,
    user_message: str,
    available_tools: list,
    state: dict,
) -> tuple[dict, list[str]]:
    """
    Run an LLM with tool-calling enabled.

    The LLM receives:
    - A system prompt describing its role
    - The user message (ticket content + context)
    - A list of available tools it can choose from

    The LLM then:
    1. Decides which tools to call (0 or more)
    2. We execute those tool calls
    3. We feed the results back to the LLM
    4. The LLM produces its final analysis JSON

    Returns:
        tuple of (result_dict, tools_used_list)
    """
    llm = get_llm()
    if llm is None:
        print(f"[SMART TOOLS] No LLM available for {agent_name}, using empty tool results")
        return {}, []

    tools_used = []
    tool_results = {}

    try:
        # ── Step 1: Bind tools to the LLM ───────────────────────────
        llm_with_tools = llm.bind_tools(available_tools)

        # ── Step 2: Ask LLM which tools to call ─────────────────────
        tool_selection_prompt = f"""{system_prompt}

AVAILABLE TOOLS:
{chr(10).join(f'- {t.name}: {t.description}' for t in available_tools)}

TICKET CONTENT:
{user_message}

First, decide which tools you need to call to gather information.
Call the appropriate tools now."""

        print(f"[SMART TOOLS] {agent_name} selecting tools dynamically...")
        response = llm_with_tools.invoke(tool_selection_prompt)

        # ── Step 3: Execute tool calls chosen by the LLM ────────────
        tool_map = {t.name: t for t in available_tools}

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                if tool_name in tool_map:
                    print(f"[SMART TOOLS] LLM selected tool: {tool_name}({tool_args})")
                    try:
                        result = tool_map[tool_name].invoke(tool_args)
                        tool_results[tool_name] = result
                        tools_used.append(tool_name)
                    except Exception as e:
                        print(f"[SMART TOOLS] Tool {tool_name} failed: {e}")
                        tool_results[tool_name] = {}
        else:
            print(f"[SMART TOOLS] {agent_name} chose not to call any tools")

    except Exception as e:
        print(f"[SMART TOOLS] Tool selection failed for {agent_name}: {e}")
        return {}, []

    return tool_results, tools_used


def parse_json_safe(text: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    try:
        return json.loads(cleaned.strip())
    except Exception:
        return {}
