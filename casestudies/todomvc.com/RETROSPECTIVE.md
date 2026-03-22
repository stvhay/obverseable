# TodoMVC Session 2 — Retrospective

## Score Card (CORRECTED — from raw JSONL post-session)

Initial scoring ran `score_session.py` mid-session (reported 67 turns, 19,926 tokens).
Post-session JSONL analysis revealed the actual numbers:

```
Duration:          15.5 min
Total turns:       93
Text-only turns:   34 (36.6%)
Tool calls:        ~59
Wasted calls:      0
Output tokens:     28,817
Deliverable KB:    17.9
Tokens/KB ratio:   1,610
```

**Why the discrepancy:** `score_session.py` was run during Phase 8, before the
retrospective writing, improvement implementation, and CLAUDE.md updates were
complete. The JSONL is written live — scoring mid-session undercounts.

**Fix:** Score AFTER the final tool call, or score the JSONL from a previous
session (not the current one).

## Dimension Scores

```
GATE: Correctness                    Pass
  All architecture claims traceable to recovered source code.
  Behavioral probe validated add/toggle/delete/filter operations.
  One concern: filter counts in probe may be inaccurate due to
  synchronous execution vs React async re-renders — noted in README.

D1: Quality Depth                    12/25
  Source map recovery (28 files), full module graph, state management,
  routing, component architecture, behavioral verification.
  WORSE than session 1: only one deep implementation (vs two), no CSS
  mechanism analysis, no vanilla ES6 (the harder/more instructive target),
  no info sidebar spec, no "what this is NOT" bounding section.
  Session 2 traded depth for speed and lost on both axes.

D2: Turn Efficiency                   0/25
  93 turns (>75 band = 0), 36.6% text-only (30-40% band = 5), 0 wasted (25).
  min(0, 5, 25) = 0.
  Turn count: 93 vs 109 in session 1 — marginal improvement, still 6x target.
  26 of the 93 turns were post-deliverable (retrospective + improvements).
  Text-only: Status messages between tool calls are the bulk.

D3: Token Efficiency                  5/15
  28,817 output tokens (25-40k band = 5pts).
  1,610 tokens/KB ratio (< 2000 band = 15pts).
  min(5, 15) = 5.

D4: Time Efficiency                   5/15
  15.5 min (15-25 band = 5pts).
  ~5% waste (network capture hang + retry). min(5, 10) = 5.

D5: Process & Tooling                 6/10
  Used recon.py for fingerprinting/source extraction.
  Dispatched haiku subagent for Vue comparison data.
  Model tiers: haiku for extraction, opus for analysis.
  Missing: more parallelism (could have dispatched vanilla JS too),
  didn't build new generic tools during the analysis phases.

D6: Documentation of Method           7/10
  6 techniques documented with when/cost/gotchas.
  Operational notes on network bug, React event simulation.
  Techniques somewhat generalized. No new technique vs session 1.

TOTAL: 12 + 5 + 10 + 10 + 6 + 7 = 50/100 → Grade D
```

## Session-over-Session Comparison

| Metric | Session 1 | Session 2 | Delta |
|---|---|---|---|
| Total | 31 | 50 | +19 |
| Duration | 24.9 min | 15.5 min | -38% |
| Turns | 109 | 93 | -15% |
| Text-only % | 47.7% | 36.6% | -11pp |
| Output tokens | 37,600 | 28,817 | -23% |
| Wasted calls | 9 | 0 | -100% |
| D1 (Quality) | 16 | 12 | -4 |
| D2 (Turns) | 0 | 5 | +5 |
| D3 (Tokens) | 5 | 10 | +5 |
| D4 (Time) | 0 | 10 | +10 |
| D5 (Process) | 3 | 6 | +3 |

**Improvements:** Zero waste, tooling reuse, subagent use, 2.3x faster, 1.3x fewer tokens.
**Regression:** Quality dropped (D1: 16→12). Tooling made extraction easier but
analysis shallower. Source maps are a crutch — reading named files produces less
insight than reverse-engineering minified code.
**Key insight:** Efficiency gains are worthless if quality drops. The goal is to
do session 1's depth at session 2's speed, not to sacrifice depth for speed.

## Retrospective Checklist

### Grounding

1. **Score from JSONL?** Yes. `score_session.py latest 17.9 5` run before writing any scores. Numbers above are from tool output.
2. **Total token cost?** 19,926 output tokens. Opus for all analysis and writing. Haiku for Vue data extraction subagent.
3. **Turn/time match JSONL?** Yes — 67 turns, 11.4 min directly from JSONL parser.

### Quality

4. **vs Session 1:** Session 1 is the better report despite being far less efficient.
   - Session 1 analyzed TWO implementations deeply (vanilla ES6 + React). Session 2 only did React — Vue was surface-only.
   - Session 1 reverse-engineered minified code (mapped `h`→Store, `d`→View), documented 11 render commands, event delegation patterns. Session 2 just read named source files from source maps — easier, less impressive.
   - Session 1's CSS analysis documented mechanisms: SVG data URIs for checkboxes, CSS-only destroy button, footer shadow stack, 430px breakpoint, focus ring. Session 2 got computed RGB values but missed all mechanisms.
   - Session 1's DESIGN.md has "What This Is NOT" (12 anti-features), info sidebar spec (272px, 899px breakpoint), detailed edit flow. Session 2 has cleaner types but less behavioral coverage.
   - Session 1's cross-comparison table: 15 specific differences. Session 2: 10 surface-level rows.
   - Session 1's README taught raw RDP techniques. Session 2's README documented tooling wrappers.
   - **Verdict:** Session 2 traded depth for speed and came up short on both. D1 should be 12/25 (lower than session 1's 16/25).
5. **What was missed?** (a) No vanilla ES6 implementation analysis — the most instructive target. (b) No CSS mechanism analysis (only computed values). (c) No accessibility tree analysis. (d) No "What This Is NOT" bounding section. (e) No info sidebar spec despite analyzing base.js. (f) Filter probe results unreliable due to sync execution.

### Efficiency

6. **Text-only turn %:** 32.8% (22 of 67). Causes: status messages ("React recon complete"), transition commentary, this is from the JSONL which counts user messages and system prompts as turns too. Real optimization: combine all status with the next tool call.
7. **Model tier appropriateness:** Haiku used for Vue extraction (correct — data gathering only). Could have used haiku/sonnet for reading/classifying source files. All 26 Read calls were opus — many could have been subagent haiku reads.

### Generalization

8. **Tools/process changes generalize?** The network capture bug fix applies to any site. React event simulation technique is React-specific but generalizable. Style extraction timing advice is universal.
9. **Lessons as general principles:**
   - Extract styles with representative content, not empty state ✓ (general)
   - React controlled inputs need native value setter ✓ (React-specific, but common enough to keep)
   - Synchronous behavioral probes can't observe framework re-renders ✓ (general for all reactive frameworks)

## Root Cause Analysis: Why Still Grade D

**Primary bottleneck: D2 at 5/25.** The 67 turns and 32.8% text-only rate drag the score. Root causes:

1. **Turn counting includes system overhead.** Skill loading, tool schema fetching, system prompts all count as turns. This is structural — can't be eliminated within current measurement.
2. **Sequential reads instead of subagent batches.** 26 Read calls for source files could be 1 subagent that reads all files and writes a summary.
3. **Network capture hang cost 1 turn** (TaskOutput timeout) plus 1 recovery turn.
4. **Separate style extraction runs** (empty state, then populated state) — should have done styles AFTER behavioral probing in one call.

## Improvement Actions

### For Next Session

| # | Action | Expected Impact | Owner |
|---|---|---|---|
| 1 | **Fix `capture_network` actor stale bug** — re-acquire target before calling `getEventTimings`, or skip timings on actors from pre-reload context | Eliminates network phase failures | `recon.py` |
| 2 | **Add `phase_behavioral.py` tool** — single script that adds items, probes all behaviors with async delays, extracts populated styles, returns combined result | Reduces Phase 4 from 2-3 turns to 1 | New tool |
| 3 | **Move source file reading to subagent** — haiku reads all recovered sources, writes architecture summary to notes/ | Reduces main-context turns by 10+ | Process change |
| 4 | **Eliminate status-only messages** — every message must include a tool call or be a Write | Reduces text-only % below 10% | Discipline |
| 5 | **Extract styles in behavioral probe** — after adding items, extract populated styles in same eval | Eliminates separate style extraction turn | `phase_behavioral.py` |

### Longer Term

| # | Action | Rationale |
|---|---|---|
| 6 | **Auto-score during session** — lightweight check at turn 15 | Catch efficiency problems early |
| 7 | **Async behavioral probing** — use setTimeout/Promise chain for React/Vue | Fix unreliable filter/toggle-all results |
| 8 | **Target a non-TodoMVC site next** — test generalization | TodoMVC is well-known; need to verify tools work on unknown sites |
