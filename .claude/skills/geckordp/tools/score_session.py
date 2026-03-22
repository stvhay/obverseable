"""
JSONL session analyzer for retrospective grading.

Usage:
    uv run python .claude/skills/geckordp/tools/score_session.py <session_id>

Reads the live JSONL (safe to run mid-session), auto-detects the end of RE
work by finding the last Write to a deliverable file (ARCHITECTURE.md,
DESIGN.md, or README.md — but not RETROSPECTIVE.md), and scores only the
turns up to that boundary.

If no deliverable Write is found, scores all turns (backwards-compatible).
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DELIVERABLE_NAMES = {"ARCHITECTURE.md", "DESIGN.md", "README.md"}


def find_jsonl(session_id):
    """Find JSONL file matching session ID prefix.

    Special values:
      "latest" — returns the most recently modified JSONL
      "list"   — prints all JSONLs sorted by mtime, returns None
    """
    base = Path.home() / ".claude" / "projects"
    all_jsonl = sorted(base.rglob("*.jsonl"), key=lambda f: f.stat().st_mtime)

    if session_id == "list":
        for f in all_jsonl:
            size = f.stat().st_size
            events = []
            with open(f) as fh:
                first = fh.readline().strip()
                if first:
                    events.append(json.loads(first))
            ts = events[0].get("timestamp", "?") if events else "?"
            print(f"  {f.name}  {size:>10,}b  started {ts}")
        return None

    if session_id == "latest":
        return all_jsonl[-1] if all_jsonl else None

    for f in all_jsonl:
        if session_id in f.name:
            return f
    # Try exact path
    p = Path(session_id)
    if p.exists():
        return p
    return None


def parse_events(path):
    """Parse JSONL into event list."""
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def find_deliverable_boundary(events):
    """Find the index of the last event that Writes a deliverable file.

    Returns the index into the events list, or None if no deliverable
    Write is found (falls back to scoring all events).
    """
    assistant_turns = [
        (i, e) for i, e in enumerate(events)
        if e.get("type") == "assistant" and "message" in e
    ]
    last_idx = None
    for event_idx, turn in assistant_turns:
        for b in turn["message"].get("content", []):
            if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                continue
            if b.get("name") != "Write":
                continue
            path = b.get("input", {}).get("file_path", "")
            basename = path.rsplit("/", 1)[-1] if "/" in path else path
            if basename in DELIVERABLE_NAMES:
                last_idx = event_idx
    return last_idx


def analyze(events):
    """Compute all metrics from events.

    Auto-detects the deliverable boundary (last Write to ARCHITECTURE.md,
    DESIGN.md, or README.md) and scores only turns up to that point.
    This makes it safe to run mid-session: the retro/grading turns that
    come after deliverable completion are excluded.
    """
    boundary = find_deliverable_boundary(events)
    if boundary is not None:
        scored_events = events[:boundary + 1]
    else:
        scored_events = events

    metrics = {}
    metrics["_boundary"] = boundary
    metrics["_total_events"] = len(events)
    metrics["_scored_events"] = len(scored_events)

    # Timestamps — use full event range start, but boundary end
    all_timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
    scored_timestamps = [e.get("timestamp") for e in scored_events if e.get("timestamp")]
    if len(scored_timestamps) >= 2:
        start = datetime.fromisoformat(all_timestamps[0].replace("Z", "+00:00"))
        end = datetime.fromisoformat(scored_timestamps[-1].replace("Z", "+00:00"))
        metrics["duration_sec"] = (end - start).total_seconds()
        metrics["duration_min"] = metrics["duration_sec"] / 60
    else:
        metrics["duration_sec"] = 0
        metrics["duration_min"] = 0

    # Assistant turns (only within scored window)
    assistant_turns = [e for e in scored_events if e.get("type") == "assistant" and "message" in e]
    metrics["total_turns"] = len(assistant_turns)

    # Text-only turns
    text_only = 0
    for turn in assistant_turns:
        content = turn["message"].get("content", [])
        has_tool = any(
            b.get("type") == "tool_use" for b in content if isinstance(b, dict)
        )
        if not has_tool:
            text_only += 1
    metrics["text_only_turns"] = text_only
    metrics["text_only_pct"] = (
        (text_only / len(assistant_turns) * 100) if assistant_turns else 0
    )

    # Tool calls
    tool_calls = []
    for turn in assistant_turns:
        for b in turn["message"].get("content", []):
            if isinstance(b, dict) and b.get("type") == "tool_use":
                tool_calls.append(b.get("name", "?"))
    metrics["total_tool_calls"] = len(tool_calls)
    metrics["tool_breakdown"] = dict(Counter(tool_calls).most_common())

    # Token usage
    total_output = 0
    for turn in assistant_turns:
        usage = turn["message"].get("usage", {})
        total_output += usage.get("output_tokens", 0)
    metrics["output_tokens"] = total_output

    # User interruptions (within scored window)
    interruptions = 0
    for e in scored_events:
        if e.get("type") == "user":
            msg = str(e.get("message", ""))
            if "interrupted" in msg.lower():
                interruptions += 1
    metrics["user_interruptions"] = interruptions

    # Errors in tool results (within scored window)
    error_count = 0
    for e in scored_events:
        if e.get("type") == "user":
            msg = e.get("message", {})
            if isinstance(msg, dict):
                for b in msg.get("content", []):
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        content = str(b.get("content", ""))
                        if "Traceback" in content or "Error:" in content or "Exit code 1" in content:
                            error_count += 1
    metrics["tool_errors"] = error_count

    # Waste detection (heuristic: Playwright, wrong imports, hung tasks)
    waste_indicators = [
        "playwright", "TabDescriptor", "npx playwright", "biih0gz8o",
    ]
    wasted = 0
    for name in tool_calls:
        if any(w in name.lower() for w in ["playwright"]):
            wasted += 1
    for turn in assistant_turns:
        for b in turn["message"].get("content", []):
            if isinstance(b, dict) and b.get("type") == "tool_use":
                cmd = str(b.get("input", {}).get("command", ""))
                if any(w in cmd for w in waste_indicators):
                    wasted += 1
    metrics["wasted_tool_calls"] = wasted

    return metrics


def score_d2(metrics):
    """D2: Turn Efficiency (0-25)."""
    turns = metrics["total_turns"]
    text_pct = metrics["text_only_pct"]
    waste = metrics["wasted_tool_calls"]

    if turns <= 15: t_score = 25
    elif turns <= 25: t_score = 20
    elif turns <= 35: t_score = 15
    elif turns <= 50: t_score = 10
    elif turns <= 75: t_score = 5
    else: t_score = 0

    if text_pct < 5: tp_score = 25
    elif text_pct < 10: tp_score = 20
    elif text_pct < 20: tp_score = 15
    elif text_pct < 30: tp_score = 10
    elif text_pct < 40: tp_score = 5
    else: tp_score = 0

    if waste == 0: w_score = 25
    elif waste <= 2: w_score = 20
    elif waste <= 4: w_score = 15
    elif waste <= 7: w_score = 10
    elif waste <= 10: w_score = 5
    else: w_score = 0

    return min(t_score, tp_score, w_score), {
        "turns": (turns, t_score),
        "text_only_pct": (f"{text_pct:.1f}%", tp_score),
        "wasted": (waste, w_score),
    }


def score_d3(metrics, deliverable_kb=0):
    """D3: Token Efficiency (0-15)."""
    tokens = metrics["output_tokens"]

    if tokens < 15000: abs_score = 15
    elif tokens < 25000: abs_score = 10
    elif tokens < 40000: abs_score = 5
    else: abs_score = 0

    if deliverable_kb > 0:
        ratio = tokens / deliverable_kb
        if ratio < 2000: ratio_score = 15
        elif ratio < 4000: ratio_score = 10
        elif ratio < 6000: ratio_score = 5
        else: ratio_score = 0
        return min(abs_score, ratio_score), {
            "tokens": (tokens, abs_score),
            "ratio": (f"{ratio:.0f} tok/KB", ratio_score),
        }

    return abs_score, {"tokens": (tokens, abs_score)}


def score_d4(metrics, waste_pct=None):
    """D4: Time Efficiency (0-15)."""
    minutes = metrics["duration_min"]

    if minutes < 10: clock_score = 15
    elif minutes < 15: clock_score = 10
    elif minutes < 25: clock_score = 5
    else: clock_score = 0

    if waste_pct is not None:
        if waste_pct < 5: w_score = 15
        elif waste_pct < 15: w_score = 10
        elif waste_pct < 30: w_score = 5
        else: w_score = 0
        return min(clock_score, w_score), {
            "minutes": (f"{minutes:.1f}", clock_score),
            "waste_pct": (f"{waste_pct:.0f}%", w_score),
        }

    return clock_score, {"minutes": (f"{minutes:.1f}", clock_score)}


def print_scorecard(metrics, deliverable_kb=0, waste_pct=None):
    """Print formatted score card."""
    print("=" * 60)
    print("SESSION SCORE CARD")
    print("=" * 60)

    boundary = metrics.get("_boundary")
    if boundary is not None:
        print(f"\nBoundary:          event {boundary} of {metrics['_total_events']} "
              f"(last deliverable Write)")
    else:
        print(f"\nBoundary:          none detected (scoring all {metrics['_total_events']} events)")

    print(f"Duration:          {metrics['duration_min']:.1f} min")
    print(f"Total turns:       {metrics['total_turns']}")
    print(f"Text-only turns:   {metrics['text_only_turns']} ({metrics['text_only_pct']:.1f}%)")
    print(f"Tool calls:        {metrics['total_tool_calls']}")
    print(f"Wasted calls:      {metrics['wasted_tool_calls']}")
    print(f"Output tokens:     {metrics['output_tokens']:,}")
    print(f"User interrupts:   {metrics['user_interruptions']}")
    print(f"Tool errors:       {metrics['tool_errors']}")

    print(f"\nTool breakdown:")
    for name, count in metrics["tool_breakdown"].items():
        print(f"  {name}: {count}")

    d2_score, d2_detail = score_d2(metrics)
    d3_score, d3_detail = score_d3(metrics, deliverable_kb)
    d4_score, d4_detail = score_d4(metrics, waste_pct)

    print(f"\n{'─' * 60}")
    print(f"DIMENSION SCORES (automatable)")
    print(f"{'─' * 60}")

    print(f"\nD2: Turn Efficiency          {d2_score:2d}/25")
    for k, (v, s) in d2_detail.items():
        print(f"    {k:20s} = {str(v):>8s}  →  {s}/25")

    print(f"\nD3: Token Efficiency         {d3_score:2d}/15")
    for k, (v, s) in d3_detail.items():
        print(f"    {k:20s} = {str(v):>8s}  →  {s}/15")

    print(f"\nD4: Time Efficiency          {d4_score:2d}/15")
    for k, (v, s) in d4_detail.items():
        print(f"    {k:20s} = {str(v):>8s}  →  {s}/15")

    auto_total = d2_score + d3_score + d4_score
    print(f"\n{'─' * 60}")
    print(f"Automatable subtotal:        {auto_total}/55")
    print(f"Manual review needed:        D1 (Quality), D5 (Process), D6 (Docs)")
    print(f"{'─' * 60}")


def main():
    if len(sys.argv) < 2:
        print("Usage: score_session.py <session_id_or_path> [deliverable_kb] [waste_pct]")
        sys.exit(1)

    path = find_jsonl(sys.argv[1])
    if not path:
        print(f"JSONL not found for: {sys.argv[1]}")
        sys.exit(1)

    deliverable_kb = float(sys.argv[2]) if len(sys.argv) > 2 else 0
    waste_pct = float(sys.argv[3]) if len(sys.argv) > 3 else None

    events = parse_events(path)
    metrics = analyze(events)
    print_scorecard(metrics, deliverable_kb, waste_pct)


if __name__ == "__main__":
    main()
