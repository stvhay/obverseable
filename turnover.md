# Obverseable — Turnover Document

## What Is This

Obverseable is a system that gives Claude (or any MCP client) full access to a browser's DevTools capabilities. It has three parts:

1. **Firefox WebExtension** — A thin bridge. When the user opens DevTools, the extension connects via WebSocket to a server and exposes the DevTools APIs as callable functions. No chat UI, no Claude integration in the extension itself. Maybe 100 lines of code.

2. **MCP Server** — Accepts WebSocket connections from browser extensions, tracks which tabs/pages are connected, and exposes everything as MCP tools. Claude Code (or any MCP client) connects to this server and gets tools to inspect, query, and act on any connected browser tab.

3. **Claude** — Connects to the MCP server via standard MCP protocol. Uses tools to read DevTools state and take actions. Not embedded in the browser — it's a separate process that talks through the MCP server.

## Architecture

```
┌─────────────┐     WebSocket     ┌─────────────┐      MCP       ┌─────────────┐
│   Firefox    │ ──────────────── │    Server    │ ─────────────  │   Claude    │
│  Extension   │   registers on   │  (MCP host)  │               │   Code      │
│  (DevTools)  │   DevTools open   │              │               │             │
└─────────────┘                   └─────────────┘               └─────────────┘
```

The extension is dumb. The server is the router. Claude is the brain.

## MCP Tools (Expected)

- `list_browsers` — what tabs/pages are connected right now
- `eval_js(tab, expression)` — run JavaScript in a page's context
- `get_network_log(tab)` — all network requests with full details
- `get_selected_element(tab)` — what's highlighted in the Elements panel
- `get_console(tab)` — recent console output (errors, warnings, logs)
- `modify_dom(tab, selector, changes)` — edit elements directly
- `get_page_info(tab)` — URL, title, meta tags, basic metrics
- More as needed — anything the DevTools API exposes can become a tool

## Key DevTools APIs (Firefox WebExtension)

- `devtools.inspectedWindow.eval()` — run JS in the inspected page
- `devtools.inspectedWindow.getResources()` — page resources (scripts, stylesheets)
- `devtools.network.getHAR()` — full HAR data for all network requests
- `devtools.network.onRequestFinished` — stream new requests as they happen
- `devtools.panels` — create the DevTools panel
- The inspected element (`$0`) is accessible via eval

## Primary Use Cases

1. **Reverse-engineering / exploring websites** (primary) — "Map out the API this site is using." "How does the auth flow work?" "What data is this page sending?" Claude reads network traffic, console output, DOM state and pieces it together.

2. **Debugging own apps** (secondary) — "Why isn't this component rendering? Check the console and network tab." Claude sees the same errors you see without copy-pasting.

## Design Decisions

- **Extension is a thin bridge, not a product** — No chat UI in the browser. Claude connects externally via MCP. This keeps the extension simple and lets you use Claude from anywhere (Claude Code, claude.ai, any MCP client).
- **Firefox-first** — Primary developer uses Firefox. Chrome port later; WebExtension APIs are ~90% compatible.
- **No API key in the extension** — The extension doesn't talk to Claude at all. It talks to your server. Claude talks to your server via MCP. Auth is between extension↔server (registration) and Claude↔server (MCP).
- **DevTools panel as primary interface** — The extension creates a panel tab in DevTools. This is where connection status lives and where the extension registers with the server. A native browser sidebar for casual (non-DevTools) use is a future possibility.

## Prior Work / Context

This project evolved from `claude-monkey`, a Tampermonkey userscript concept. During ideation we realized:
- A userscript hits a ceiling — can't access DevTools APIs, CDP, or debugger
- A browser extension removes that ceiling entirely
- But embedding Claude chat in the extension is unnecessary complexity
- The cleanest architecture is: dumb extension bridge → MCP server → Claude connects externally

The old repo (`stvhay/claude-monkey`) had ~42 issues for the userscript approach. All are obsolete. The new architecture is simple enough to plan from scratch.

There is also a `stvhay/skynet` project (mesh server for AI agents) that could potentially serve as the MCP server, or the MCP server could be standalone.

## Tech Stack

- **Extension**: Vanilla JavaScript, Firefox WebExtension APIs, WebSocket client
- **MCP Server**: TBD — needs to be a WebSocket server + MCP-compatible endpoint
- **No build step for the extension** — keep it simple, vanilla JS

## Name

"Obverseable" — a portmanteau of "obverse" (the other side) and "observable." Claude sees your browser from the other side.

## Repo

https://github.com/stvhay/obverseable
