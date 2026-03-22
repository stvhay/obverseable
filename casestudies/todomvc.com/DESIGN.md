# TodoMVC Design Specification

Behavioral specification of the React TodoMVC implementation, sufficient for reimplementation.

## Data Model

```typescript
interface Todo {
  id: string;       // nanoid(21), charset: A-Za-z0-9_-
  title: string;    // Trimmed, HTML-entity-escaped, min 2 chars
  completed: boolean;
}

type State = Todo[];  // Initial: []
```

## Actions

```typescript
type Action =
  | { type: "ADD_ITEM"; payload: { title: string } }
  | { type: "UPDATE_ITEM"; payload: { id: string; title: string } }
  | { type: "REMOVE_ITEM"; payload: { id: string } }
  | { type: "TOGGLE_ITEM"; payload: { id: string } }
  | { type: "TOGGLE_ALL"; payload: { completed: boolean } }
  | { type: "REMOVE_ALL_ITEMS" }
  | { type: "REMOVE_COMPLETED_ITEMS" };
```

**Reducer semantics (pure function, no side effects):**

| Action | Reducer Logic |
|---|---|
| `ADD_ITEM` | `state.concat({ id: nanoid(), title, completed: false })` |
| `UPDATE_ITEM` | Map: match by id, replace title |
| `REMOVE_ITEM` | `state.filter(todo => todo.id !== id)` |
| `TOGGLE_ITEM` | Map: match by id, flip `completed` |
| `TOGGLE_ALL` | Map: set all `completed` to payload value |
| `REMOVE_ALL_ITEMS` | Return `[]` |
| `REMOVE_COMPLETED_ITEMS` | `state.filter(todo => !todo.completed)` |

Unknown action types throw `Error("Unknown action: {type}")`.

## URL Routing

Hash-based routing. Three routes:

| URL Hash | Filter | Visible Todos |
|---|---|---|
| `#/` | All | Full `todos` array |
| `#/active` | Active only | `todos.filter(t => !t.completed)` |
| `#/completed` | Completed only | `todos.filter(t => t.completed)` |

Default route: `#/` (all). Wildcard catch-all renders the app for any unrecognized hash.

## Component Behavior

### Header

- Displays `<h1>todos</h1>` as page title
- Contains the new-todo Input component

### Input (reusable)

- `<input>` with class `new-todo`, id `todo-input`
- Wrapped in `<div class="input-container">` with hidden `<label>` for accessibility
- **Submit:** Enter key. Trims value, validates `length >= 2`, sanitizes HTML entities (`& < > " ' /`), calls `onSubmit`, clears input
- **Blur:** Calls optional `onBlur` callback (used in edit mode)
- **No submit on blur** in new-todo mode (only in edit mode, where blur cancels)
- **Auto-focus:** `autoFocus` attribute

### Main

- Renders only when `visibleTodos.length > 0`:
  - Toggle-all checkbox (`<input class="toggle-all">` + `<label class="toggle-all-label">`)
  - Todo list (`<ul class="todo-list">`)
- Toggle-all checked state: `visibleTodos.every(t => t.completed)`
- Toggle-all onChange: dispatches `TOGGLE_ALL` with `e.target.checked`

### Item (memoized with `React.memo`)

**View mode (default):**
- `<li>` with class `completed` when `todo.completed`
- `<div class="view">` containing:
  - `<input class="toggle" type="checkbox">` — checked = `completed`, onChange → `TOGGLE_ITEM`
  - `<label>` — displays title, onDoubleClick → enter edit mode
  - `<button class="destroy">` — onClick → `REMOVE_ITEM`

**Edit mode (after double-click):**
- Replaces entire `<div class="view">` with Input component
- `defaultValue` = current title
- Submit (Enter): if title empty → `REMOVE_ITEM`, else → `UPDATE_ITEM`, exit edit mode
- Blur: exit edit mode (cancel, no save)
- **Note:** Edit mode uses `isWritable` local state, not a CSS class swap

### Footer

- **Hidden** when `todos.length === 0` (returns null)
- **Todo count:** `"{n} item(s) left!"` where n = active (non-completed) count. Singular "item" when n === 1
- **Filter links:** Three `<a>` tags inside `<ul class="filters">`:
  - `href="#/"` → All
  - `href="#/active"` → Active
  - `href="#/completed"` → Completed
  - Selected link gets class `selected` based on current route
- **Clear completed:** `<button class="clear-completed">Clear completed</button>`
  - `disabled` when `activeTodos.length === todos.length` (no completed items)
  - onClick → `REMOVE_COMPLETED_ITEMS`

## Persistence

**None.** State is in-memory only. No localStorage, no sessionStorage, no server persistence. Refresh resets to empty state.

## Visual Design

### Layout

| Property | Value |
|---|---|
| Page background | `rgb(245, 245, 245)` / `#f5f5f5` |
| App max-width | `550px` |
| App min-width | `230px` |
| App centering | `margin: 0 auto` |
| App top margin | `130px` |
| App bottom margin | `40px` |
| App background | `rgb(255, 255, 255)` / white |
| App shadow | `0 2px 4px rgba(0,0,0,0.2), 0 25px 50px rgba(0,0,0,0.1)` |
| App position | `relative` |

### Typography

| Element | Font | Size | Weight | Color |
|---|---|---|---|---|
| Body | Helvetica Neue, Helvetica, Arial, sans-serif | 14px | 300 | `rgb(17, 17, 17)` |
| H1 "todos" | Same family | 80px | 200 | `rgb(184, 63, 69)` |
| New-todo input | Same family | 24px | 300 | inherit |
| Footer info | Same family | 11px | 300 | `rgb(77, 77, 77)` |
| Footer info links | Same family | 11px | 400 | `rgb(77, 77, 77)` |

### Key Dimensions

| Element | Height | Padding |
|---|---|---|
| New-todo input | 65px | `16px 16px 16px 60px` |
| Header | 65px | 0 |

### Effects

| Element | Effect |
|---|---|
| H1 | `position: absolute`, centered above app |
| New-todo input | `box-shadow: inset 0 -2px 1px rgba(0,0,0,0.03)` |
| Filter link (selected) | `border: 1px solid rgb(206, 70, 70)` |
| Info section | `margin-top: 65px`, `text-align: center` (implied by base CSS) |

### CSS Sources

- `todomvc-app-css/index.css` — Canonical TodoMVC component styles (app, header, main, footer, items, filters)
- `todomvc-common/base.css` — Page-level layout (body, learn bar, info footer)
- `todo/app.css` — App-specific overrides (if any)

## Edge Cases

| Scenario | Behavior |
|---|---|
| Empty input (Enter) | No todo added (min 2 chars after trim) |
| Whitespace-only input | No todo added (trimmed to empty) |
| Single character | No todo added (< 2 chars) |
| HTML in input | Entity-escaped: `<` → `&lt;`, `>` → `&gt;`, etc. |
| Edit to empty | Todo deleted (REMOVE_ITEM) |
| Edit blur | Cancels edit, reverts to view mode |
| Toggle-all when mixed | Sets all to checked (completed) |
| Toggle-all when all completed | Sets all to unchecked (active) |
| Clear completed when none completed | Button disabled |
| Unknown reducer action | Throws Error |

## Shared Infrastructure Contract

Every TodoMVC implementation must:

1. Include `base.js` which expects:
   - `learn.json` fetchable from site root
   - Optional `[data-framework]` attribute on a DOM element for framework identification
   - Google Analytics conditional on `todomvc.com` hostname
2. Use `todomvc-app-css` for consistent visual appearance
3. Use class names: `.todoapp`, `.header`, `.new-todo`, `.main`, `.toggle-all`, `.todo-list`, `.footer`, `.todo-count`, `.filters`, `.clear-completed`
4. Use hash-based routing with `#/`, `#/active`, `#/completed`
