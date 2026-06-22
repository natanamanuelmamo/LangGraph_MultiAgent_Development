"""
Analytics Dashboard (BONUS) — prints aggregate statistics after running scenarios.

Computes escalation rate, resolution rate, category/priority breakdowns,
confidence stats, tool usage, and routing path metrics.
"""

from collections import Counter


def print_analytics(results: list[dict]) -> None:
    """Print a formatted analytics summary from a list of final ticket states."""
    # Filter out errored runs
    valid = [r for r in results if "error" not in r]
    total = len(valid)

    if total == 0:
        print("\n[ANALYTICS] No valid results to analyse.")
        return

    escalated = sum(1 for r in valid if r.get("escalation_required", False))
    resolved = sum(1 for r in valid if r.get("resolved", False))

    categories = Counter(r.get("category", "Unknown") for r in valid)
    priorities = Counter(r.get("priority", "unknown") for r in valid)

    confidences = [r.get("confidence_score", 0.0) for r in valid]
    avg_confidence = sum(confidences) / len(confidences)

    all_tools: list[str] = []
    for r in valid:
        all_tools.extend(r.get("tools_used", []))
    tool_counts = Counter(all_tools)

    path_lengths = [len(r.get("routing_path", [])) for r in valid]
    min_hops = min(path_lengths) if path_lengths else 0
    max_hops = max(path_lengths) if path_lengths else 0
    avg_hops = sum(path_lengths) / len(path_lengths) if path_lengths else 0

    # -- Print dashboard ----------------------------------------------
    print("\n" + "=" * 70)
    print("  ANALYTICS DASHBOARD")
    print("=" * 70)
    print(f"  Total Tickets Processed  : {total}")
    print(f"  Escalation Rate          : {escalated}/{total} ({escalated / total * 100:.1f}%)")
    print(f"  Resolution Rate          : {resolved}/{total} ({resolved / total * 100:.1f}%)")
    print()

    print("  -- Category Breakdown -----------------------------")
    for cat, count in categories.most_common():
        bar = "#" * (count * 4)
        print(f"    {cat:<22s} : {count}  {bar}")
    print()

    print("  -- Priority Breakdown -----------------------------")
    for pri, count in priorities.most_common():
        bar = "#" * (count * 4)
        print(f"    {pri:<22s} : {count}  {bar}")
    print()

    print(f"  Avg Confidence Score     : {avg_confidence:.2f}")
    print()

    print("  -- Tool Usage -------------------------------------")
    for tool_name, count in tool_counts.most_common():
        print(f"    {tool_name:<30s} : {count} calls")
    print()

    print("  -- Routing Path Stats -----------------------------")
    print(f"    Min hops : {min_hops}")
    print(f"    Max hops : {max_hops}")
    print(f"    Avg hops : {avg_hops:.1f}")
    print("=" * 70)
