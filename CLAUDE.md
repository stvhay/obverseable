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

- **Do not stop** except at step 6 (asking for feedback).
- **Git tree must be clean at the end** apart from the case study report. Ask the user whether to commit the report (they may want to delete it for a repeat session).
- **Everything persists in the repo** — CLAUDE.md, PROCESS.md, RUBRIC.md, tool code. Memory files are deleted between sessions.
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
│   ├── recon.py                # RDPSession context manager — connect, navigate, fingerprint, sources
│   ├── score_session.py        # JSONL session analyzer — D2/D3/D4 auto-scoring
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

- Always run `/finishing-a-development-branch` before merging to ensure documentation is updated and version bumps are correct.
- Screenshot actor must be accessed from root (`root.get_root()["screenshotActor"]`), not from target.
- `evaluate_js_async` is two-stage — register listener BEFORE calling, match results by `resultID`.
- Network methods fail silently without `watcher.watch_resources()` first.
- `inner_html()`/`outer_html()` return LongString for large pages — use `StringActor.substring()` to page through.
- `navigate_to()` and `reload()` destroy the window global — monkey-patches installed via eval don't survive. Use `ScriptInjector` from `tools/inject.py` to inject JS before page scripts run.
- Large JS eval results (e.g., `JSON.stringify` of big arrays) return as LongString grips, not strings. Always check for `{"type": "longString"}` and resolve via `StringActor`.
- After navigation, always re-acquire the target — the old `consoleActor` and other actor IDs become stale. `RDPSession.navigate()` handles this automatically.
