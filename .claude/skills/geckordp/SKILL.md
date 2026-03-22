---
name: geckordp
description: "Use when writing Python code that controls Firefox via RDP, building MCP tools wrapping Firefox DevTools, looking up geckordp actor methods or response shapes, debugging geckordp connections, or inspecting browser state (DOM, network, storage, console, debugger)."
---

# geckordp — Firefox DevTools RDP Reference

## Task Selection

Given a goal, read these references in order:

| Goal | Read |
|---|---|
| Connect to Firefox | `00-connection.md` |
| Run JavaScript in page | `04-web-console.md` |
| Inspect/modify DOM | `07a-inspector.md` → `07b-walker.md` → `07c-node.md` |
| Capture network traffic | `08-network.md` |
| Read/write cookies or storage | `11-storage.md` |
| Set breakpoints, step through code | `05-thread-debugger.md` → `06-source-actor.md` |
| Take screenshots | `09-screenshot.md` |
| Navigate tabs, reload pages | `14-window-global.md` |
| Disable cache, override UA | `15-configuration.md` |
| Profile memory | `10-memory.md` |
| Debug geckordp itself | `19-settings-debug.md` |

## Reference Files

| File | Contents |
|---|---|
| `00-connection.md` | Firefox setup, prefs, connection pattern |
| `01-rdp-client.md` | RDPClient API, listeners, send/receive |
| `02-root-actor.md` | RootActor — tabs, processes, workers |
| `03-tab-actor.md` | TabActor — get_target, get_watcher |
| `04-web-console.md` | WebConsoleActor — JS eval, messages |
| `05-thread-debugger.md` | ThreadActor — breakpoints, stepping |
| `06-source-actor.md` | SourceActor — source text, breakpoint positions |
| `07a-inspector.md` | InspectorActor — walker, styles, highlighters |
| `07b-walker.md` | WalkerActor — DOM traversal, manipulation, mutations |
| `07c-node.md` | NodeActor, NodeListActor — element info, node object structure |
| `08-network.md` | Watcher, NetworkParent/Content/Event |
| `09-screenshot.md` | ScreenshotActor — capture from root |
| `10-memory.md` | MemoryActor, HeapSnapshotActor |
| `11-storage.md` | Cookie, LocalStorage, SessionStorage, IndexedDB, Cache |
| `12-preference-device.md` | PreferenceActor, DeviceActor |
| `13-accessibility.md` | Accessibility, AccessibleWalker, Simulator |
| `14-window-global.md` | WindowGlobalActor — navigation, frames |
| `15-configuration.md` | TargetConfiguration, ThreadConfiguration |
| `16-events.md` | Events enum — all event types |
| `17-string-actor.md` | StringActor — LongString consumer |
| `18-descriptors.md` | Process, Worker, WebExtension, Addons |
| `19-settings-debug.md` | GECKORDP settings, env vars, logging |

## Test Harness

Integration tests are in `tests/test_*.py`. They run against a live Firefox instance and validate every documented capability. Run with:

```bash
FIREFOX_HOST=192.168.64.1 FIREFOX_PORT=6000 uv run pytest tests/ -v --timeout=30
```

## Tools

Reusable Python utilities in `tools/`:

| Tool | Purpose | Generality |
|---|---|---|
| `recon.py` | `RDPSession` context manager — connect, navigate, fingerprint, classify scripts, extract styles, extract source maps, capture network | Any site |
| `inject.py` | `ScriptInjector` — inject JS before page scripts via debugger firstStatement pause | Any site |
| `phase_recon.py` | Phases 0-2 in one script: navigate, fingerprint, classify, extract sources, capture network, extract styles | Any site |
| `score_session.py` | JSONL session analyzer — computes D2/D3/D4 rubric metrics | Any session |
| `grades_db.py` | SQLite store for per-session scores and raw metrics | Any session |

## Key Patterns

### Two-Stage Async Eval
`evaluate_js_async()` returns a `resultID` immediately. The actual result arrives via actor listener. Always register a listener BEFORE calling eval.

### Watcher-First for Network
Must call `watcher.watch_resources([Resources.NETWORK_EVENT])` before any network methods work.

### Screenshots from Root
Use `root.get_root()["screenshotActor"]`, NOT `target["screenshotContentActor"]`.

### LongString via StringActor
`inner_html()`/`outer_html()` return LongString objects for large content. Use `StringActor.substring(start, end)` to page through the full content.
