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

**Output:** Write to `notes/surface.json`

**Use `tools/fingerprint.py` when available.**

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

Programmatic interaction via JS eval to verify architecture hypotheses:

1. Add items via DOM manipulation
2. Toggle, edit, delete items
3. Test routing/filtering
4. Check state after each action
5. Test edge cases (empty input, XSS payloads, rapid operations)

**Single script with sequential actions and state checks between each.**

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

### Phase 8: Retrospective (< 3 min, 2 turns)

1. Run `.claude/skills/geckordp/tools/score_session.py <session_id> <deliverable_kb> <waste_pct>`
2. Record scores via `.claude/skills/geckordp/tools/grades_db.py`
3. Write RETROSPECTIVE.md with metrics, lessons, follow-up actions
4. **Cleanup check:** Verify no operational knowledge leaked to `~/.claude/projects/.../memory/`. All knowledge ships in the repo (CLAUDE.md, PROCESS.md, RUBRIC.md). Delete any memory files created during the session.

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
| Retrospective | 2 |

### Rules

1. **Never produce a text-only turn** unless answering a user question. Every turn should include at least one tool call.
2. **Batch RDP operations.** One connection, multiple evals. Never open/close connection for a single query.
3. **Subagents write to files.** Never return large data to main context.
4. **Read before writing.** Don't guess APIs — invoke the skill, read the reference.
5. **No reinventing wheels.** If a tool exists in `tools/`, use it.
6. **Always read JSONL at the end.** Ground truth for retrospective. Don't reflect from memory.

### Model Tier Strategy

Haiku and sonnet are cheaper and faster but less capable. They make mistakes — always verify their output.

| Task | Model | Verify How |
|---|---|---|
| Source extraction | haiku | Check file count matches expected, spot-check first/last file |
| Network capture | haiku | Check capture.json is valid JSON, has expected URL patterns |
| DOM tree walk | haiku | Grep output for known selectors (.todoapp, etc.) |
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
