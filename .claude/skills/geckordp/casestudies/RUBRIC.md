# RE Session Grading Rubric

## Design Principles

This rubric produces a **score vector**, not a scalar. A single number hides what to fix. Each dimension has measurable thresholds that tell you exactly where to invest effort.

Correctness is a **gate**: if the gate fails, the session score is capped regardless of efficiency. You can be slow and correct (acceptable), but fast and wrong is worse than not running at all.

All metrics marked `[JSONL]` can be extracted automatically from the session log. Metrics marked `[REVIEW]` require reading the deliverables.

## Gate: Correctness (Pass/Fail)

The gate evaluates whether the deliverables are trustworthy enough to act on. **If any gate criterion fails, the overall session grade is capped at D regardless of other scores.**

| Criterion | Pass | Fail |
|---|---|---|
| **Factual accuracy** | All stated facts verified against source/behavior | Any claim contradicted by evidence |
| **Completeness of data model** | All fields, types, and constraints documented | Missing fields that affect behavior |
| **Behavioral coverage** | All user-visible features specified with trigger → behavior | Missing features discoverable by interacting with the app |
| **Reproducibility** | A competent developer could reimplement from DESIGN.md alone | Spec requires reading the original source to fill gaps |
| **No hallucination** | Every architectural claim traceable to source or behavioral observation | Architecture described that doesn't exist in the code |

**How to evaluate:** Re-read DESIGN.md and ARCHITECTURE.md. For each claim, ask: "what evidence produced this?" If the answer is "I assumed" or "I remember from training data," the gate fails.

## Dimension 1: Quality Depth (0–25 points)

Beyond the gate, how thorough and insightful is the analysis?

| Points | Criteria |
|---|---|
| 0–5 | Surface only: lists scripts, DOM structure, basic features |
| 6–10 | Architecture recovered: module graph, state management pattern, data flow |
| 11–15 | Behavioral edge cases documented, cross-implementation comparison, CSS/visual spec |
| 16–20 | Non-obvious findings: security properties, performance characteristics, framework-imposed vs app-chosen patterns, undocumented API surface |
| 21–25 | Insights the original developers would find valuable: bugs found, design flaws identified, improvement opportunities, patterns transferable to other projects |

**Optimization signal:** If stuck at 0–10, you're doing data extraction without analysis. If stuck at 11–15, you're describing but not evaluating.

## Dimension 2: Turn Efficiency (0–25 points)

`[JSONL]` — fully automatable.

| Points | Total Turns | Text-Only Turn % | Wasted Tool Calls |
|---|---|---|---|
| 25 | ≤ 15 | < 5% | 0 |
| 20 | 16–25 | 5–10% | 1–2 |
| 15 | 26–35 | 10–20% | 3–4 |
| 10 | 36–50 | 20–30% | 5–7 |
| 5 | 51–75 | 30–40% | 8–10 |
| 0 | > 75 | > 40% | > 10 |

**Score = min(turn_score, text_only_score, waste_score)** — weakest link determines the grade.

**Definitions:**
- *Turn*: One assistant message (with or without tool calls)
- *Text-only turn*: Assistant turn with zero tool calls (pure commentary)
- *Wasted tool call*: Tool call that produced no information used in deliverables, OR a retry of a failed call that could have been avoided by reading documentation first

**Optimization signal:** High turns + low text-only% = too many small scripts (batch them). High text-only% = chattiness (combine commentary with action). High waste = not reading refs before coding.

## Dimension 3: Token Efficiency (0–15 points)

`[JSONL]` — fully automatable.

| Points | Output Tokens | Tokens per Deliverable KB |
|---|---|---|
| 15 | < 15,000 | < 2,000 |
| 10 | 15,000–25,000 | 2,000–4,000 |
| 5 | 25,000–40,000 | 4,000–6,000 |
| 0 | > 40,000 | > 6,000 |

**Score = min(absolute_score, ratio_score)**

*Tokens per deliverable KB* = total output tokens / total KB of final deliverable files (DESIGN.md + ARCHITECTURE.md + README.md). This measures signal-to-noise: how many tokens were spent to produce each KB of useful output.

**Optimization signal:** High absolute + low ratio = producing good output but writing too much commentary. High ratio + low absolute = too little output for the tokens spent (excessive retries, errors).

## Dimension 4: Time Efficiency (0–15 points)

`[JSONL]` — automatable from timestamps.

| Points | Wall Clock | Waste Phase % |
|---|---|---|
| 15 | < 10 min | < 5% |
| 10 | 10–15 min | 5–15% |
| 5 | 15–25 min | 15–30% |
| 0 | > 25 min | > 30% |

**Score = min(clock_score, waste_score)**

*Waste phase %* = time spent on approaches that were abandoned (wrong tool, wrong API, retrying errors) / total session time.

**Optimization signal:** High clock + low waste = inherently complex target (acceptable). High waste% = procedural failures (read the docs, use the tooling).

## Dimension 5: Process & Tooling (0–10 points)

`[JSONL]` + `[REVIEW]`

| Points | Criteria |
|---|---|
| 0–2 | No reuse of existing tools. Reinvented connection boilerplate. |
| 3–4 | Used existing tools where available. Built new tools for gaps. |
| 5–6 | Effective subagent use. Model tier strategy applied (haiku for extraction, opus for analysis). |
| 7–8 | Subagents wrote to files. Main context stayed focused on analysis. Parallelism exploited. |
| 9–10 | Tools built this session are generic enough for next session. Process improvements documented. |

**Optimization signal:** Score < 5 means attention is being wasted on mechanics instead of analysis. Score < 8 means parallelism opportunities are being missed.

## Dimension 6: Documentation of Method (0–10 points)

`[REVIEW]`

| Points | Criteria |
|---|---|
| 0–2 | README.md lists what was done but not how. |
| 3–5 | Techniques catalogued with when-to-use and cost. |
| 6–8 | Techniques include gotchas, failure modes, and workarounds discovered. Operational notes for future sessions. |
| 9–10 | Techniques are generalized beyond this target. New technique discovered not in prior sessions. RETROSPECTIVE.md has actionable improvement items with clear ownership. |

**Optimization signal:** Score < 5 means the session produced artifacts but not learning. The whole point of meta-RE is that each session improves the next.

## Scoring

```
GATE: Correctness                    Pass / Fail
  If Fail → overall grade = D, stop.

D1: Quality Depth                    ___/25
D2: Turn Efficiency                  ___/25
D3: Token Efficiency                 ___/15
D4: Time Efficiency                  ___/15
D5: Process & Tooling                ___/10
D6: Documentation of Method          ___/10
                                     -------
TOTAL                                ___/100
```

| Grade | Score | Meaning |
|---|---|---|
| A | 85–100 | Excellent. Process is mature. Focus on harder targets. |
| B | 70–84 | Good. 1–2 dimensions need work. Review lowest scores. |
| C | 55–69 | Adequate. Multiple dimensions underperforming. Build tooling before next session. |
| D | < 55 or gate fail | Significant problems. Fix fundamentals before attempting next target. |

## Applying the Rubric

### During session (lightweight self-check)

At natural milestones, ask:
1. Am I past turn 15? If yes, am I in the writing phase yet? If not, I'm behind.
2. Have I produced any text-only turns in the last 5? If yes, batch my next commentary with a tool call.
3. Am I about to write a claim in a deliverable? What's my evidence?

### Post-session (full evaluation)

1. Parse JSONL for D2, D3, D4 metrics (automate this)
2. Read deliverables for gate and D1
3. Review tool calls for D5
4. Review README.md/RETROSPECTIVE.md for D6
5. Score each dimension
6. Identify the **two lowest-scoring dimensions** — these are the improvement targets for next session
7. Write concrete actions for each (not "do better" — "build X tool" or "change Y step in process")

### Session-over-session tracking

Append to a tracking table:

```
| Session | Target | Gate | D1 | D2 | D3 | D4 | D5 | D6 | Total | Grade | Key Fix |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 001 | TodoMVC | Pass | 15 | 0 | 0 | 0 | 2 | 7 | 24 | D | Build tooling, reduce turns |
| 002 | ??? | | | | | | | | | | |
```

## Retroactive Score: Session 001 (TodoMVC)

```
GATE: Correctness                    Pass
  (One concern: Vue comparison missing from ARCHITECTURE.md despite claiming it.
   Minor — doesn't invalidate other findings. Gate passes with note.)

D1: Quality Depth                    16/25
  Source map recovery, full architecture, cross-framework comparison (partial),
  behavioral verification, CSS spec. Missing: accessibility, perf analysis,
  security beyond XSS escaping.

D2: Turn Efficiency                   0/25
  109 turns (>75), 47.7% text-only (>40%), 9 wasted calls (>8).
  All three sub-scores at floor.

D3: Token Efficiency                  5/15
  ~37,600 output tokens (25k-40k band = 5pts).
  Deliverables ~18KB → ratio ~2,089 tokens/KB (2k-4k band = 10pts).
  min(5, 10) = 5.

D4: Time Efficiency                   5/15
  24.9 min (15-25 band = 5pts).
  32% waste phase (>30% = 0pts).
  min(5, 0) = 0. Corrected: 0/15.

D5: Process & Tooling                 3/10
  No subagents. No model tiers. Built recon.py after session (counts partial).
  No parallelism.

D6: Documentation of Method           7/10
  9 techniques catalogued with when/cost/gotchas. Operational notes good.
  RETROSPECTIVE.md written with metrics. Techniques somewhat generalized.
  Missing: new technique vs prior art comparison (first session, so N/A).

TOTAL: 16 + 0 + 5 + 0 + 3 + 7 = 31/100 → Grade D
```

**Lowest dimensions:** D2 (Turn Efficiency: 0), D4 (Time Efficiency: 0)
**Root cause for both:** No tooling, no process, 8 minutes of wrong-tool fumbling, excessive turns.
**Fix for next session:** Use recon.py, invoke skill immediately, batch operations, target ≤15 turns.
