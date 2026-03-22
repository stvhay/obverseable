# TodoMVC React — Architecture

## Overview

Single-page todo application built with React (function components + hooks), bundled with Webpack. No backend, no persistence. State lives in-memory via `useReducer` and resets on reload.

**URL:** `https://todomvc.com/examples/react/dist/`

## Module Graph

```
index.js                         Entry point
├── react, react-dom             Framework (bundled)
├── react-router-dom             HashRouter for filtering
├── todomvc-app-css/index.css    Shared TodoMVC styles
├── todomvc-common/base.css      Base reset styles
└── todo/app.jsx                 Root component
    ├── todo/reducer.js          State transitions (useReducer)
    │   └── todo/constants.js    Action type strings
    ├── todo/app.css              App-specific overrides
    └── components/
        ├── header.jsx           Title + input
        │   └── input.jsx        Shared input (sanitize + validate)
        ├── main.jsx             Todo list + toggle-all
        │   └── item.jsx         Single todo (memo-wrapped)
        │       └── input.jsx    Reused for edit mode
        └── footer.jsx           Count + filters + clear-completed
```

## Scripts (3 loaded)

| Script | Role | Notes |
|---|---|---|
| `app.bundle.js` | App | Webpack bundle, source maps available (28 files recovered) |
| `base.js` | Shared infra | TodoMVC learn sidebar, Google Analytics, `learn.json` fetcher |
| `analytics.js` | Analytics | Google Analytics (loaded by base.js on todomvc.com) |

## State Management

**Pattern:** `useReducer` with plain action objects — no Redux, no Context API.

```
State shape: Todo[]
Todo: { id: string, title: string, completed: boolean }
```

Single reducer in `reducer.js` handles 7 action types:

| Action | Payload | Effect |
|---|---|---|
| `ADD_ITEM` | `{title}` | Appends new todo with nanoid-generated ID |
| `UPDATE_ITEM` | `{id, title}` | Updates title of matching todo |
| `REMOVE_ITEM` | `{id}` | Filters out matching todo |
| `TOGGLE_ITEM` | `{id}` | Flips `completed` on matching todo |
| `TOGGLE_ALL` | `{completed}` | Sets all todos to given completed state |
| `REMOVE_COMPLETED_ITEMS` | (none) | Filters out completed todos |
| `REMOVE_ALL_ITEMS` | (none) | Returns empty array |

**ID generation:** Embedded nanoid v3 (non-secure, Math.random, 21-char IDs from URL-safe alphabet).

## Routing

`react-router-dom` HashRouter wrapping the entire app. Routes: `#/`, `#/active`, `#/completed`.

Filtering happens in `Main` component via `useMemo` on `useLocation().pathname`:
- `/` → all todos
- `/active` → `!todo.completed`
- `/completed` → `todo.completed`

Footer renders filter links as `<a href="#/...">` with `classnames({selected: route === "..."})`.

## Data Flow

```
User action → DOM event → dispatch(action) → reducer → new state → React re-render
```

All components receive `dispatch` via props (no Context). `todos` state array is the single source of truth, held in `App` component.

**Memoization strategy:**
- `Item` wrapped in `React.memo` for referential equality checks
- `useMemo` for `visibleTodos` (filtered list) and `activeTodos` (count)
- `useCallback` for all event handlers passed to children

## Input Processing

`Input` component (shared between header and edit mode):
1. Trims whitespace
2. Validates minimum length (2 characters)
3. Sanitizes via manual HTML entity escaping (`& < > " ' /`)
4. Calls `onSubmit` callback
5. Clears input value

**Security note:** Double-encoded XSS — React already escapes JSX text content, and the app additionally HTML-encodes before storing. Result: `<img>` displays as `&lt;img&gt;` in source but renders correctly due to React's built-in escaping. The manual sanitize function is redundant but not harmful.

## Build & Bundle

- **Bundler:** Webpack (evidenced by source map format with `webpack://` prefixes)
- **Source maps:** Available, 28 files including `node_modules` sources
- **CSS:** Combined `app.css` (7389 chars) with charset directive, includes both TodoMVC shared styles and app-specific overrides
- **Dependencies (from source map):** react, react-dom, react-router-dom, classnames, scheduler, history

## Shared Infrastructure (base.js)

The `base.js` script is TodoMVC's shared learn sidebar:
1. Fetches `learn.json` from site root
2. Renders sidebar with framework info, links, issue count
3. Injects Google Analytics (UA-31081062-1) on todomvc.com hostname
4. Includes micro-template engine (underscore-style `<%= %>`)
5. Redirects `tastejs.github.io` → `todomvc.com`

## Persistence

**None.** No `localStorage`, no `sessionStorage`, no cookies, no API calls. State resets completely on page reload. The `REMOVE_ALL_ITEMS` action exists but is never triggered by UI.
