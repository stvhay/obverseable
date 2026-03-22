# TodoMVC Architecture

## System Overview

TodoMVC is a **framework comparison showcase** — a single landing site linking to 40+ independent todo app implementations, each built with a different JS framework. Every implementation follows a shared specification, shared CSS, and shared infrastructure layer (`base.js`).

```
todomvc.com (landing)           → jQuery + Bootstrap directory
  └── /examples/{framework}/    → Independent SPA per framework
        ├── app bundle          → Framework-specific implementation
        ├── base.js             → Shared: learn sidebar, analytics, issue counter
        ├── todomvc-app-css     → Shared: canonical TodoMVC stylesheet
        └── todomvc-common      → Shared: base styles, fonts
```

## Landing Page

**Stack:** jQuery 1.x, Bootstrap 3, Web Components polyfill (`webcomponents-lite.min.js`), PrefixFree (CSS vendor prefix removal).

**Purpose:** Framework directory with category tabs (New, Labs, Compile-to-JS), popover descriptions on hover, rotating developer quotes, social share buttons (Twitter, Google+).

**Key module:** `main.js` (6KB) — jQuery plugin `persistantPopover` for framework hover cards, `Quotes` object for animated quote rotation (25s cycle), `AppTabs` for iron-select Web Component tab switching.

**External scripts:** Google Analytics (ga.js), Google+ API, Twitter widgets — social/analytics, no app logic.

## React Implementation (`/examples/react/dist/`)

### Module Graph

```
index.js (entry)
  ├── react, react-dom
  ├── react-router-dom (HashRouter, Routes, Route)
  ├── todomvc-app-css/index.css
  ├── todomvc-common/base.css
  └── todo/app.jsx
        ├── todo/reducer.js
        │     └── todo/constants.js (action types)
        ├── todo/components/header.jsx
        │     └── todo/components/input.jsx
        ├── todo/components/main.jsx
        │     ├── todo/components/item.jsx
        │     │     └── todo/components/input.jsx
        │     └── classnames
        └── todo/components/footer.jsx
              └── classnames
```

28 files recovered from source maps (webpack bundle).

### State Management

**Pattern:** `useReducer` — single reducer at App level, dispatch passed via props.

**State shape:** `Todo[]` where `Todo = { id: string, title: string, completed: boolean }`.

**ID generation:** nanoid (non-secure, 21-char alphanumeric, inlined from ai/nanoid@3.0.2).

**Actions (7):**

| Action | Payload | Effect |
|---|---|---|
| `ADD_ITEM` | `{ title }` | Append new todo with nanoid() |
| `UPDATE_ITEM` | `{ id, title }` | Update title by id |
| `REMOVE_ITEM` | `{ id }` | Filter out by id |
| `TOGGLE_ITEM` | `{ id }` | Flip completed |
| `TOGGLE_ALL` | `{ completed }` | Set all to completed value |
| `REMOVE_ALL_ITEMS` | — | Return `[]` |
| `REMOVE_COMPLETED_ITEMS` | — | Filter out completed |

**No persistence.** State resets on refresh — no localStorage, no sessionStorage, no server sync.

### Routing

**Mechanism:** `react-router-dom` HashRouter. Single wildcard route (`path="*"`) renders `<App />`.

**Filter routes:** `useLocation().pathname` reads `/`, `/active`, `/completed`. Filtering happens in `Main` component via `useMemo` over todos array.

| Hash | Filter |
|---|---|
| `#/` | All todos |
| `#/active` | `!todo.completed` |
| `#/completed` | `todo.completed` |

### Component Architecture

| Component | Props | Responsibilities |
|---|---|---|
| `App` | — | Owns state (`useReducer`), renders Header/Main/Footer |
| `Header` | `dispatch` | Renders h1 "todos" + Input for new items |
| `Input` | `onSubmit, placeholder, label, defaultValue, onBlur` | Reusable controlled input. Sanitizes HTML, min 2 chars, Enter to submit |
| `Main` | `todos, dispatch` | Filter by route, render toggle-all + Item list |
| `Item` | `todo, dispatch, index` | `memo`'d. View mode (toggle/label/destroy) or edit mode (Input). Double-click to edit |
| `Footer` | `todos, dispatch` | Count, filter links, clear completed (disabled when none completed) |

### Input Sanitization

`Input` component has client-side HTML entity escaping: `& < > " ' /` → HTML entities. This is defense-in-depth; React's JSX already escapes output. Minimum input length: 2 characters after trim.

### Build

**Bundler:** Webpack. Source maps available (`app.bundle.js.map`). 28 source files recovered including webpack runtime modules.

## Shared Infrastructure: `base.js`

Minified ~3.7KB script loaded by every implementation. Responsibilities:

1. **Learn sidebar** — Fetches `learn.json` from site root, renders framework metadata (documentation links, source links, issue count) via underscore-style template engine
2. **Google Analytics** — Conditional on `todomvc.com` hostname. UA-31081062-1
3. **GitHub issues** — XHR to GitHub API, displays open issue count for the implementation
4. **Hostname redirect** — Redirects `tastejs.github.io` → `todomvc.com`

Template engine is a vendored subset of Underscore.js (`_.template`).

## Vue Implementation (`/examples/vue/dist/`)

**Stack:** Vue 3 (detected via `__VUE__` and `data-v-app`). Vite build (hashed JS module: `index-ebzV244v.js`, CSS: `index-AN23XS_-.css`). No source maps recovered (Vite production build strips them by default).

**Same shared infra:** `base.js`, todomvc-app-css, todomvc-common.

**Same routing pattern:** Hash-based (`#/`, `#/active`, `#/completed`).

**Same DOM structure:** `.todoapp` > header/main/footer, `.todo-list li`, `.filters`, `.toggle-all`.

## Cross-Implementation Comparison

| Aspect | React | Vue |
|---|---|---|
| Framework version | React 18+ (hooks API) | Vue 3 (Composition API) |
| Build tool | Webpack | Vite |
| Script loading | Classic `<script>` | ES Module (`type="module"`) |
| Source maps | Yes (28 files) | No |
| State management | `useReducer` | Vue reactivity |
| Routing | react-router-dom HashRouter | Vue Router (hash mode) |
| CSS strategy | Webpack CSS imports | Vite CSS extraction |
| Persistence | None | None |
| Shared infra | base.js | base.js |

## Data Flow

```
User Input → Header/Input → dispatch(ADD_ITEM) → todoReducer → new state
                                                        ↓
URL Hash Change → useLocation() → Main filters todos → re-render
                                                        ↓
Toggle/Delete/Edit → Item → dispatch(action) → todoReducer → new state
```

Unidirectional data flow: App owns state, passes `dispatch` down, children call `dispatch` with action objects, reducer produces new state, React re-renders.
