# Obverseable

A Claude Code skill for operating Firefox via the Remote Debugging Protocol (RDP). Gives Claude direct access to every Firefox DevTools capability — JS evaluation, network inspection, DOM traversal, debugger control, screenshots, storage, memory profiling — through the geckordp Python library.

## Architecture

```
Firefox (user's browser)  --TCP/RDP-->  Claude Code (via geckordp skill)
       port 6000                         reads reference docs + runs Python
```

Single connection. No extension, no server, no intermediary. Claude connects directly to Firefox's RDP port using geckordp and operates DevTools programmatically.

## What This Project Is

1. **Skill reference material** (`.claude/skills/geckordp/`) — comprehensive, tested documentation of every geckordp actor, method, parameter, and wire format
2. **Integration test harness** (`tests/`) — 104 tests validating every capability against a live Firefox instance
3. **Case studies** (planned) — worked examples of black-box reverse engineering using the skill

## Tech Stack

- Python 3.13+, geckordp library
- Nix flake for dev environment (uv, ruff, pytest)
- Firefox with `--start-debugger-server` enabled

## Firefox Connection

RDP host and port are in `rdp-host.txt` (gitignored) at project root. Format: `host:port` on one line (e.g., `192.168.64.1:6000`). Read this file to get connection details — don't ask the user.

## Build & Test

```bash
# Install dependencies
uv sync --extra dev

# Run tests against live Firefox (must be running with RDP enabled)
FIREFOX_HOST=192.168.64.1 FIREFOX_PORT=6000 uv run pytest tests/ -v --timeout=30

# Firefox setup: set these in about:config, then launch with --start-debugger-server 6000
#   devtools.debugger.remote-enabled = true
#   devtools.debugger.force-local = false
#   devtools.debugger.prompt-connection = false
#   devtools.chrome.enabled = true
```

## Case Study Exercises

When the user wants to run an exercise (e.g., "run an exercise on example.com"):

1. **Create `casestudies/{target}/` directory tree** with `raw/`, `notes/`, etc.
2. **Reverse engineer the site** using the geckordp skill and `tools/recon.py`. Use whatever techniques needed. Goal: produce documentation sufficient for a fresh context to reproduce the entire design (without plagiarising source — reconstruct requirements, constraints, features, behavior).
3. **Write deliverables** in `casestudies/{target}/` — ARCHITECTURE.md, DESIGN.md, README.md, RETROSPECTIVE.md. Sub-deliverables are encouraged.
4. **Grade the session** using the rubric in `casestudies/RUBRIC.md`. Score from JSONL via `tools/score_session.py`. Record in `tools/grades_db.py`. The rubric is fixed.
5. **Comprehensive self-evaluation.** Develop actionable recommendations (not "do better" — concrete changes to tools, process, docs).
6. **Ask for user feedback.** This is the ONE stop point. Adjust recommendations based on feedback.
7. **Implement all recommendations** — tool improvements, process doc updates, bug fixes, etc.

### Rules

- **Do not stop** except at step 6 (asking for feedback). This includes step 7 — after getting feedback, implement ALL recommendations and audit ALL affected docs without asking "is that it?" or "should I continue?" Push through to completion autonomously. The user should not have to prompt you to keep going.
- **Git tree must be clean at the end** apart from the case study report. Ask the user whether to commit the report (they may want to delete it for a repeat session).
- **Everything persists in the repo** — CLAUDE.md, PROCESS.md, RUBRIC.md, tool code. Memory files are deleted between sessions. If a lesson matters, it goes in CLAUDE.md or PROCESS.md, not memory.
- **Use `RDPSession`** from `tools/recon.py` — don't reinvent connection boilerplate. The skill and tools can be modified.
- **DESIGN.md must be reimplementable** — a developer should be able to rebuild the app from it alone.

### Process Reference

- `.claude/skills/geckordp/casestudies/PROCESS.md` — phase-by-phase playbook with turn budgets and efficiency constraints
- `.claude/skills/geckordp/casestudies/RUBRIC.md` — 6-dimension grading rubric (gate + D1–D6)

### Output Structure

```
casestudies/{target}/
├── README.md           # RE methodology log — techniques, findings, operational notes
├── ARCHITECTURE.md     # System structure — modules, data flow, dependencies
├── DESIGN.md           # Behavioral spec — sufficient for reimplementation
├── RETROSPECTIVE.md    # Efficiency analysis from JSONL, lessons, follow-ups
├── raw/
│   ├── sources/        # Original source files from source maps
│   ├── network/        # Network capture JSON
│   └── screenshots/    # Page screenshots
└── notes/              # Working files (surface.json, dom.json, etc.)
```

## Skill Structure

```
.claude/skills/geckordp/
├── SKILL.md                    # Skill entry point (with frontmatter)
├── tools/
│   ├── recon.py                # RDPSession — connect, navigate, fingerprint, classify scripts, extract styles, source maps, network
│   ├── inject.py               # ScriptInjector — pre-page JS injection via debugger pause
│   ├── phase_recon.py          # Phases 0-2 in one script — any site (navigate, fingerprint, sources, network, styles)
│   ├── quality_review.py       # D1 quality review panel — dispatches haiku/sonnet/opus reviewers
│   ├── score_session.py        # JSONL session analyzer — D2/D3/D4 auto-scoring, boundary-aware
│   └── grades_db.py            # SQLite grades store — session-over-session tracking
├── casestudies/
│   ├── PROCESS.md              # 8-phase RE methodology playbook
│   ├── RUBRIC.md               # 6-dimension grading rubric
│   └── grades.db               # SQLite database of session scores
└── references/
    ├── 00-connection.md        # Firefox setup, connection pattern
    ├── 01-rdp-client.md        # RDPClient API, listeners
    ├── 02-root-actor.md        # Tabs, processes, workers
    ├── 03-tab-actor.md         # Target, watcher
    ├── 04-web-console.md       # JS eval (two-stage async)
    ├── 05-thread-debugger.md   # Breakpoints, stepping
    ├── 06-source-actor.md      # Source text, breakpoint positions
    ├── 07a-inspector.md        # InspectorActor — walker, styles, highlighters
    ├── 07b-walker.md           # WalkerActor — DOM traversal, manipulation
    ├── 07c-node.md             # NodeActor, NodeListActor
    ├── 08-network.md           # Network capture with bodies
    ├── 09-screenshot.md        # Page/element screenshots
    ├── 10-memory.md            # Memory profiling, heap snapshots
    ├── 11-storage.md           # Cookies, localStorage, IndexedDB
    ├── 12-preference-device.md # Firefox prefs, device info
    ├── 13-accessibility.md     # A11y tree, color blindness sim
    ├── 14-window-global.md     # Navigation, frames, tab control
    ├── 15-configuration.md     # Cache, UA, JS toggle, DPR
    ├── 16-events.md            # All event types for listeners
    ├── 17-string-actor.md      # LongString content retrieval
    ├── 18-descriptors.md       # Process, Worker, Extension actors
    └── 19-settings-debug.md    # geckordp debug logging
```

## Workflow (Accelerated)

CI, version bumping, and changelog enforcement are temporarily suspended to accelerate development. Plans are optional — use when helpful, skip when overhead exceeds value.

**Still enforced:**
- TDD — write tests, verify against live browser
- Verification before completion — evidence before assertions
- SPEC.md for subsystems — codify invariants and failure modes
- Documentation — keep skill reference files current

**Suspended:**
- CI pipeline checks
- Version bump / changelog maintenance
- Mandatory implementation plans
- PR template checklist

**Process:**
1. File a GitHub issue when tracking is useful
2. Branch for isolation when needed (`/using-git-worktrees`)
3. Brainstorm if the problem space is unclear (`/brainstorming`)
4. Write tests first, then implement
5. Verify with evidence before claiming done
6. Self-review before merging (`/requesting-code-review`)

## Writing Standards

- Structured, dense, no filler
- Lead with the point, then supporting detail
- Code comments only where logic isn't self-evident

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution workflow.

## Lessons Learned

### RDP / geckordp
- Always run `/finishing-a-development-branch` before merging to ensure documentation is updated and version bumps are correct.
- Screenshot actor must be accessed from root (`root.get_root()["screenshotActor"]`), not from target.
- `evaluate_js_async` is two-stage — register listener BEFORE calling, match results by `resultID`.
- Network methods fail silently without `watcher.watch_resources()` first.
- `inner_html()`/`outer_html()` return LongString for large pages — use `StringActor.substring()` to page through.
- `navigate_to()` and `reload()` destroy the window global — monkey-patches installed via eval don't survive. Use `ScriptInjector` from `tools/inject.py` to inject JS before page scripts run.
- Large JS eval results (e.g., `JSON.stringify` of big arrays) return as LongString grips, not strings. Always check for `{"type": "longString"}` and resolve via `StringActor`.
- After navigation, always re-acquire the target — the old `consoleActor` and other actor IDs become stale. `RDPSession.navigate()` handles this automatically.
- `extract_source_map()` fails on large bundles — `fetch_text()` returns LongString grip. Use stash pattern: `fetch(url).then(r=>r.text()).then(t=>{window.__sm=t})`, parse source list in-browser.
- `eval_json()` now handles LongString grips automatically (fixed session 5). Previously it returned the raw LongString dict instead of resolving it. Pages with >50 scripts or >10KB JSON results trigger this.
- For GitHub repo pages, skip DOM scraping for file contents — use `fetch()` to `raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`. GitHub's file viewer is a React component with unpredictable DOM structure.

### Case Study Process
- **Never score from memory.** Run `score_session.py` FIRST, paste output, then write analysis. Self-estimates are off by 3-7x. Session 2 estimated 14 turns / Grade B; actual was 76 turns / Grade D. This error is structural — every session repeats it. Only the tooling fix (boundary-aware scorer reading live JSONL) prevents it.
- **Analyze ALL loaded scripts**, not just the app bundle. Support files (analytics loaders, sidebar injectors, config fetchers) reveal shared infrastructure and host page contracts.
- **DESIGN.md must include visual design values.** Extract computed styles programmatically — colors, fonts, dimensions, breakpoints. Without these the spec fails the reproducibility gate.
- **Text-only turns are the primary efficiency leak.** Every assistant message must include at least one tool call. Status goes alongside tool calls, never standalone.
- **Batch all parallel tool calls into one message.** 8 file reads = 1 message, not 8.
- **Validate subagent output programmatically** before trusting it. Check for required keys, non-null values.
- **Network event actors go stale after reload.** `capture_network(action="reload")` collects actor IDs from pre-reload context. Use short timeout (2s) for `getEventTimings`/`getResponseHeaders` and skip failures silently.
- **Computed styles show values, not mechanisms.** `getComputedStyle` gives RGB colors and pixel sizes — but not SVG data URIs, box-shadow stacks, pseudo-element content, or CSS-only visibility tricks. For a reproducible DESIGN.md, fetch and analyze the actual CSS source to document *how* things are built, not just what they look like.
- **Verify algorithm claims against source.** Never document an algorithm (search, chunking, merge) from exports or interface files alone. Read the implementation file. Session 5 documented RRF search from `search/__init__.py` without reading `search/search.py` — all three reviewers flagged this.
- **Fetch config implementations, not just examples.** Config example files are always a subset of actual config. Session 5 missed RerankerConfig, AsrConfig, EnrichmentConfig, chunk_overlap_tokens because only `config.example.json` was read, not `config.py`.
- **Include design evaluation.** DESIGN.md must critically evaluate at least 3 design decisions. Absence of bugs/risks/trade-offs is a scoring penalty — all three session 5 reviewers flagged this.
- **RE the application, not the content.** The target is the web application at the URL — its UI components, interactive elements, behaviors. Session 5 documented the content a page displayed but not the page itself. Content is context; the page's UI is the target.

### Tooling Principles
- **Build capabilities, not macros.** After a bad session, the instinct is to script the specific steps that were slow. That produces tools that only work on one site. Instead, identify what general capability was missing and build that. Test: "would this tool do anything useful on a site I've never seen?" If no, it's not a tool.
- **Behavioral probing is inherently target-specific.** There is no general "behavioral probe" script — every site has different selectors, interactions, and assertions. Write probes fresh each session from general primitives (step-chain with setTimeout for framework re-renders, native input setter for React/Vue, click/type/wait helpers).
- **Extract styles on populated pages.** Computed style extraction returns `found: false` for selectors that match dynamically-created content. Run style extraction after interacting with the page, not on initial load.
- **Reactive framework input: use native setter.** `input.value = x` doesn't trigger React/Vue. Use `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(input, x)` then dispatch `input` event.
- **Async probing for reactive frameworks.** Synchronous DOM reads between dispatched events miss React/Vue re-renders. Chain operations with `setTimeout` (100ms) to let the framework reconcile.
