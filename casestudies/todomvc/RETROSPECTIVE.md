# TodoMVC React — Session 4 Retrospective

## Score Card (from `score_session.py`)

```
Boundary:          event 176 of 238 (last deliverable Write)
Duration:          4.2 min
Total turns:       43
Text-only turns:   10 (23.3%)
Tool calls:        33
Wasted calls:      0
Output tokens:     9,336
User interrupts:   1
Tool errors:       1

Tool breakdown: Read: 25, Bash: 5, Write: 3

D2: Turn Efficiency          10/25
    turns                =       43  →  10/25
    text_only_pct        =    23.3%  →  10/25
    wasted               =        0  →  25/25

D3: Token Efficiency         15/15
    tokens               =     9336  →  15/15

D4: Time Efficiency          15/15
    minutes              =      4.2  →  15/15

Automatable subtotal:        40/55
```

## Quality Review Panel (D1)

| Reviewer | Score | Key Finding |
|---|---|---|
| Haiku | 18/25 | Missing analysis of *why* design choices were made (conditional render vs CSS class), no cross-implementation comparison, no accessibility coverage |
| Sonnet | 21/25 | Toggle-all scoping discrepancy noted as actionable, edit mode unverified by probe, no performance characterization |
| Opus | 17/25 | Unused `index` prop in Item is dead code, `data-testid` testing infrastructure undocumented, edit-to-empty is unreachable through UI (min-length-2 blocks it), CSS cascade not analyzed |

**Median D1: 18/25**

### Errors Found by Panel

1. **Edit-to-empty unreachable (Opus):** DESIGN.md lists "Edit to empty string → Item removed" but the shared Input component enforces min-length-2, so this code path is dead. The deliverable marks it as "Source code" verified, which is technically honest but misleading.
2. **autoFocus scope (Sonnet):** DESIGN.md states Input has autoFocus set without qualifying that this applies to all instances — the edit-mode Input gets it too, which may not be intended.
3. **CSS scope understated (Opus):** ARCHITECTURE.md calls app.css "app-specific overrides" but it contains the full combined CSS including shared TodoMVC styles and learn sidebar styles.

## Final Scores

```
GATE: Correctness                    Pass
D1: Quality Depth                    18/25  (panel median)
D2: Turn Efficiency                  10/25  (43 turns, 23.3% text-only)
D3: Token Efficiency                 15/15  (9,336 tokens)
D4: Time Efficiency                  15/15  (4.2 min)
D5: Process & Tooling                 7/10
D6: Documentation of Method           7/10
                                     -------
TOTAL                                72/100  Grade B
```

## Retrospective Checklist

### Grounding

1. **Did you run `score_session.py` first?** Yes. Output pasted above. 43 turns, 4.2 min, 9336 output tokens.
2. **Token cost?** 9,336 output tokens (within scored boundary). Model: Claude Opus 4.6 for main session, haiku/sonnet/opus for quality review panel.
3. **Do turn count and wall-clock match JSONL?** Yes — 43 turns, 4.2 min, verified from scorer output.

### Quality (from panel)

4. **Panel D1 scores:** Haiku 18, Sonnet 21, Opus 17. Median: 18.
5. **Errors/missing identified by panel:**
   - Edit-to-empty is unreachable (dead code path documented as behavior)
   - Unused `index` prop in Item component
   - `data-testid` attributes undocumented
   - No cross-implementation comparison
   - No accessibility audit
   - No performance characterization
   - CSS cascade not analyzed (shared vs app-specific)
   - autoFocus applies to all Input instances, not just header

   **Fixable now:** Edit-to-empty caveat, CSS scope description, autoFocus qualifier. Not fixable without more work: cross-comparison, accessibility, performance.

### Efficiency

6. **Text-only turns:** 10/43 (23.3%). Several were status updates between phases. Most could have been eliminated by combining status text with the next tool call.
7. **Model tiers:** Quality review panel used haiku/sonnet/opus correctly. Main session was all opus — the 25 Read calls could have been batched more aggressively (all source files in one message instead of two).

### Generalization

8. **Tools and process changes:** All tools used (phase_recon.py, phase_behavioral.py, quality_review.py, score_session.py, grades_db.py) are generic. No target-specific modifications needed.
9. **Lessons stated as general principles:** Yes — see below.

## Comparison to Session 1

| Metric | Session 1 | Session 4 | Improvement |
|---|---|---|---|
| Turns | 109 | 43 | 2.5x fewer |
| Text-only % | 47.7% | 23.3% | 2x better |
| Duration | 24.9 min | 4.2 min | 5.9x faster |
| Output tokens | 37,600 | 9,336 | 4x fewer |
| D1 (Quality) | 16 | 18 | +2 |
| D2 (Turns) | 0 | 10 | +10 |
| D3 (Tokens) | 5 | 15 | +10 |
| D4 (Time) | 0 | 15 | +15 |
| Total | 31 | 72 | +41 (D→B) |

## Lessons Learned

1. **`phase_recon.py` is the right starting point.** It handles 3 phases in one tool call. The behavioral probe adds the remaining verification in one more call. Two script executions cover 80% of data gathering.

2. **Text-only turns are still the primary efficiency leak.** 23.3% is better than 47.7% but still costs 5 points. Every status message should accompany a tool call. The fix is discipline, not tooling.

3. **Batch all Read calls.** 25 reads across multiple messages. Could be 2 messages: one for all source files, one for probe/style/network data. This alone would cut ~8 turns.

4. **Panel reviewers find real bugs.** Opus found the edit-to-empty unreachability, unused `index` prop, and CSS cascade issue — all missed by the session. The panel is worth the 3 agent dispatches.

5. **Edit mode detection probe needs update.** The behavioral probe's `editingWorks` check assumes `.editing` CSS class. This React implementation uses conditional rendering. The probe should also check for Input component within `.view` after double-click.

## Follow-up Actions

| Action | Type | Priority |
|---|---|---|
| Fix `phase_behavioral.py` edit detection to check for Input within `.view` | Tool fix | High |
| Combine status messages with tool calls — eliminate standalone text turns | Process | High |
| Batch all source file reads into single messages | Process | Medium |
| Add cross-implementation comparison dispatch to process | Process | Medium |
| Add accessibility probing to behavioral script | Tool enhancement | Low |
