# Obverseable

Obverseable gives Claude (or any MCP client) full access to a browser's DevTools capabilities via three components: a Firefox WebExtension (thin bridge), an MCP Server (router), and Claude Code (brain).

## Architecture

```
Firefox Extension  --WebSocket-->  MCP Server  --MCP-->  Claude Code
(DevTools bridge)                  (Python)              (any MCP client)
```

- **Extension**: Vanilla JavaScript, Firefox WebExtension APIs, WebSocket client. No build step.
- **MCP Server**: Python. Accepts WebSocket connections from extensions, exposes DevTools as MCP tools.
- **Claude**: Connects via standard MCP protocol. Not embedded in the browser.

## Tech Stack

- Extension: Vanilla JS, Firefox WebExtension APIs
- Server: Python
- No build step for the extension

## Build & Test

<!-- TODO: fill in as project develops -->

```bash
# Server
# pip install -e .
# pytest

# Extension
# Load as temporary add-on in Firefox: about:debugging → Load Temporary Add-on
```

## Workflow

1. File a GitHub issue (bug report or feature request template)
2. Create a feature branch (`/using-git-worktrees` for isolation)
3. Brainstorm the design (`/brainstorming`)
4. Write an implementation plan (`/writing-plans`)
5. Execute the plan (`/executing-plans`)
6. Verify with evidence before claiming done
7. Self-review (`/requesting-code-review`)
8. Open a PR using the template

## Writing Standards

- Structured, dense, no filler
- Lead with the point, then supporting detail
- Code comments only where logic isn't self-evident

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution workflow.

## Lessons Learned

- Always run `/finishing-a-development-branch` before merging to ensure documentation is updated and version bumps are correct.
