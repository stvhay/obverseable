# RE Case Study Process

Repeatable playbook for black-box reverse engineering a website via Firefox RDP, producing specification-grade documentation and self-improvement artifacts.

## Inputs

- Target URL
- Firefox running with RDP enabled on known host:port
- geckordp skill invoked

## Outputs (per target site)

```
casestudies/{target}/
├── README.md           # RE methodology log — techniques used, findings, operational notes
├── ARCHITECTURE.md     # System structure — modules, data flow, dependencies, patterns
├── DESIGN.md           # Behavioral spec — sufficient for reimplementation
├── RETROSPECTIVE.md    # Efficiency analysis from JSONL, lessons, follow-up actions
├── raw/                # Raw extracted artifacts (source files, source maps, network captures)
│   ├── sources/        # Original source files recovered from source maps
│   ├── network/        # Network capture JSON
│   └── screenshots/    # Page screenshots
└── notes/              # Working notes (subagent output files)
```

## Phases

### Phase 0: Setup (< 1 min, 1 turn)

1. Invoke geckordp skill
2. Create target directory: `casestudies/{target}/` with `raw/sources/`, `raw/network/`, `notes/`
3. Connect to Firefox, confirm tab access

**Single script. No separate turns for each step.**

### Phase 1: Surface Recon (< 2 min, 1-2 turns)

Single script that navigates to target and extracts in one eval:
- Document metadata (title, charset, content-type, doctype)
- All `<script>` elements (src, type, content length)
- All `<link>` and `<style>` elements
- All `<meta>` tags
- Framework markers (React, Vue, Angular, Svelte, jQuery, Backbone)
- Storage state (localStorage, sessionStorage, cookies)
- Custom window globals
- First 50 `<a href>` links
- `document.cookie`, `document.referrer`
- **Interactive UI elements:** All `<button>`, `<input>`, `<select>`, `<details>`, `<dialog>` elements. Elements with click handlers or `role="button"`. Tab bars, navigation menus, dropdowns, modals.

**Output:** Write to `notes/surface.json`

**Use `tools/fingerprint.py` when available.**

**IMPORTANT: The target is the web application at the URL, not the content it displays.** RE the application's UI and behavior — the content is context, not the target.

### Phase 2: Source Recovery (< 3 min, 1-2 turns)

For each script discovered in Phase 1:

1. Fetch script source via `fetch().then(t => window.__s = t)`
2. Check for `sourceMappingURL` comment
3. If source map exists: fetch it, extract `sources` and `sourcesContent`
4. Write original source files to `raw/sources/`

**Dispatch subagents (haiku) for parallel extraction if multiple bundles.** Each subagent writes to files, not back to main context.

**Use `tools/source_maps.py` when available.**

### Phase 3: Architecture Analysis (< 3 min, 1 turn of thinking)

From recovered sources, identify:
- Module dependency graph
- State management pattern (Redux, MobX, useReducer, plain objects, etc.)
- Routing mechanism
- Data model shape
- Event handling strategy
- Persistence mechanism
- Build tool and bundling strategy

**This is analysis, not data gathering. Minimize tool calls. Read source files from disk, think, write.**

### Phase 4: Behavioral Probing (< 3 min, 1-2 turns)

Programmatic interaction via JS eval to verify architecture hypotheses. Write a custom probe script per target based on what Phase 1-2 discovered. There is no general behavioral probe — every site has different interactions, selectors, and assertions.

General approach:
1. **Inventory all interactive elements** — buttons, tabs, dropdowns, toggles, forms, navigation links, expand/collapse controls. This is the primary output: a map of every user action the page supports.
2. Write a single async script that performs each action with `setTimeout` delays for framework re-renders
3. After each action, read DOM state to verify the expected change
4. Test edge cases relevant to this specific target
5. Extract computed styles on the now-populated page

**The probe must cover the page's UI, not just its content.** Every clickable/interactive element is a behavioral specification to document.

**Use the step-chain pattern (Promise + setTimeout) for reactive frameworks. Use native input setters for React/Vue controlled inputs. Write the probe fresh — don't reuse a previous target's script.**

### Phase 5: Network & DOM Analysis (< 2 min, 1 turn)

1. Set up watcher, reload page, capture all network traffic
2. Walk DOM tree via InspectorActor for structural verification
3. Write network capture to `raw/network/capture.json`

**Can dispatch as subagent in background during Phase 4.**

### Phase 6: Cross-Implementation Comparison (optional, < 5 min)

If the target has multiple implementations (like TodoMVC):

1. **Dispatch parallel subagents** (one per implementation)
2. Each subagent: navigate, fingerprint, extract sources, write to `notes/{framework}.json`
3. Main agent: read results, produce comparison table

**This is the primary parallelism opportunity. Use haiku agents for data extraction, opus for analysis.**

### Phase 7: Write Deliverables (< 5 min, 3 turns)

1. **ARCHITECTURE.md** — from Phase 3 analysis + Phase 2 sources
2. **DESIGN.md** — from Phase 4 behavioral verification + Phase 3 architecture
3. **README.md** — from all phases, documenting techniques used

**Write all three in sequence. Each is one turn (one Write call).**

### Phase 7.5: Quality Review Panel (< 2 min, 1 turn)

Dispatch three agents (haiku, sonnet, opus) in parallel to independently score D1 (Quality Depth) against the rubric. Each agent reads the deliverables and the rubric — nothing else. No self-assessment.

**Tool:** `.claude/skills/geckordp/tools/quality_review.py <target_dir>` generates the review prompt. Dispatch with:

```
Agent(model="haiku",  prompt=<review_prompt>)
Agent(model="sonnet", prompt=<review_prompt>)
Agent(model="opus",   prompt=<review_prompt>)
```

**Use median score as D1.** Record all three scores in RETROSPECTIVE.md.

**Why this exists:** Self-assessment is structurally broken. Session 2 estimated D1=17, Grade B (72/100). Actual panel score: D1=15, Grade D (44/100). Every session overestimates quality by 20-30 points when scoring from memory. The panel eliminates ego from the measurement.

**Bonus:** The reviewers find bugs and gaps the author missed. Opus found 6 real bugs in session 3's deliverables that the session itself missed entirely (duplicate HTML IDs, dead code, wrong DOM claims, legacy API, toggle-all scoping, double-encoding mislabeled as defense-in-depth).

### Phase 8: Retrospective (< 3 min, 2 turns)

1. Run `.claude/skills/geckordp/tools/score_session.py latest <deliverable_kb> <waste_pct>` — the scorer auto-detects the deliverable boundary and reads the live JSONL safely
2. Collect quality review panel results (from Phase 7.5). Use **median** for D1.
3. Record scores via `.claude/skills/geckordp/tools/grades_db.py`
4. Answer the **retrospective checklist** (below) — paste answers into RETROSPECTIVE.md
5. Write RETROSPECTIVE.md with metrics, panel scores, checklist answers, lessons, follow-up actions
6. **Cleanup check:** Verify no operational knowledge leaked to `~/.claude/projects/.../memory/`. All knowledge ships in the repo (CLAUDE.md, PROCESS.md, RUBRIC.md). Delete any memory files created during the session.

### Retrospective Checklist

Answer every question using evidence (JSONL output, file contents, git log), not memory. If the answer reveals a problem, say so — the checklist exists to catch failures before they ship.

**Grounding**
1. Did you run `score_session.py` and paste its output before writing any scores? What were the actual numbers?
2. What was the total token cost (input + output)? What model(s) were used and for what proportion of the work?
3. Do the turn count and wall-clock time in your retrospective match the JSONL? (Check, don't estimate.)

**Quality (from panel, not self-assessment)**
4. What were the three panel D1 scores (haiku, sonnet, opus)? What is the median? Paste the scores — do not paraphrase.
5. What errors or missing items did the panel reviewers identify? List all unique findings across the three reviews. Which ones are fixable in the deliverables right now?

**Efficiency**
6. What percentage of your turns were text-only (no tool calls)? What were they doing — could any have been eliminated or merged with tool calls?
7. Were model tiers used appropriately? Could any opus work have been done by sonnet or haiku?

**Generalization**
8. Do the tools and process changes you're proposing work on any website, or only this target? If target-specific, delete them or demote to notes.
9. Are the lessons learned stated as general principles, or as target-specific observations? Rewrite any that don't generalize.

## Efficiency Constraints

### Turn Budget

Target: **< 20 turns total** for a standard site.

| Phase | Max Turns |
|---|---|
| Setup | 1 |
| Surface recon | 2 |
| Source recovery | 2 |
| Architecture analysis | 1 |
| Behavioral probing | 2 |
| Network/DOM | 1 |
| Cross-comparison | 3 (subagent dispatch + collect) |
| Write deliverables | 3 |
| Quality review panel | 1 (dispatch 3 agents) |
| Retrospective | 2 |

### Rules

1. **Never produce a text-only turn** unless answering a user question. Every turn should include at least one tool call. Status updates go alongside tool calls, never as standalone messages.
2. **Batch RDP operations.** One connection, multiple evals. Never open/close connection for a single query.
3. **Subagents write to files.** Never return large data to main context.
4. **Read before writing.** Don't guess APIs — invoke the skill, read the reference.
5. **No reinventing wheels.** If a tool exists in `tools/`, use it.
6. **Always read JSONL at the end.** Run `score_session.py` FIRST, paste its output into RETROSPECTIVE.md, then write analysis. Never estimate scores from memory — self-perception is systematically wrong by 3-7x.
7. **Batch parallel tool calls.** All independent Read/Bash calls go in one message. Reading 8 files = 1 message with 8 reads, not 8 messages.
8. **Write behavioral probes fresh per target.** There is no reusable probe script — every site has different selectors and interactions. Write a single async eval per target from general primitives (step-chain, native input setter, click/wait). Return one result object. Never split into separate eval calls.
9. **Analyze ALL loaded scripts.** After fingerprinting, categorize every script (app code, framework, shared infrastructure, analytics, polyfill). Analyze all "shared infrastructure" files — they often define the host page contract. Don't skip support files.
10. **Extract visual design programmatically.** One eval call to get computed styles for key elements (colors, fonts, dimensions, borders, shadows). DESIGN.md without visual design values fails the reproducibility gate.
11. **Validate subagent output before trusting it.** Check: file exists, valid JSON, no null/false for required keys. If validation fails, re-run with sonnet. Don't debug haiku failures.
12. **Verify algorithm claims against source.** For any algorithmic claim in DESIGN.md (search algorithm, chunking strategy, merge logic), the source file implementing it must have been read. "Inferred from exports" is not sufficient — fetch the implementation.
13. **Fetch config implementation, not just examples.** Config example files are always a subset of the actual config schema. For Python projects, read the config dataclass/class definition. For JS projects, read the schema validation code.
14. **Include design evaluation in DESIGN.md.** Add a "Design Evaluation" section that critically evaluates at least 3 design decisions — bugs, risks, trade-offs, improvement opportunities. Absence of critique is a scoring penalty.

### Model Tier Strategy

Haiku and sonnet are cheaper and faster but less capable. They make mistakes — always verify their output.

| Task | Model | Verify How |
|---|---|---|
| Source extraction | haiku | Check file count matches expected, spot-check first/last file |
| Network capture | haiku | Check capture.json is valid JSON, has expected URL patterns |
| DOM tree walk | haiku | Grep output for known selectors from fingerprint |
| Fingerprinting | haiku | Check all expected keys present in output JSON |
| Cross-framework data gathering | sonnet | Compare output structure across frameworks for consistency |
| Architecture analysis | opus | — (main agent judgment) |
| Design spec writing | opus | — (main agent judgment) |
| Retrospective | opus | — (requires full session context) |

**Rule:** If a subagent's output looks wrong or incomplete, re-run with sonnet instead of haiku. If still wrong, pull into main context with opus. Don't spend turns debugging subagent failures.

## Improvement Loop

```
Session N
├── RE target site
├── Produce deliverables
├── Read JSONL, write RETROSPECTIVE.md
├── Identify tooling gaps → build tools
├── Identify doc gaps → update skill references
└── Choose next target (increasing complexity)

Session N+1
├── Load improved tooling
├── RE next target
├── Compare metrics to Session N
└── Repeat
```

## Target Selection Criteria

Progress from simple to complex:

1. **Static site, no framework** — baseline (done: TodoMVC landing page)
2. **SPA, known framework, source maps available** — (done: TodoMVC ES6/React)
3. **SPA, framework, no source maps** — forces pure black-box analysis
4. **SPA with API backend** — network analysis becomes critical
5. **SPA with auth** — session management, token handling
6. **Complex production app** — multiple bundles, code splitting, service workers
