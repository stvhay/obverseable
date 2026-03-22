# TodoMVC React — Design Specification

Behavioral specification sufficient for reimplementation. All values derived from source code analysis and programmatic behavioral probing.

## Data Model

```typescript
interface Todo {
  id: string;       // nanoid(21), URL-safe alphabet [A-Za-z0-9_-]
  title: string;    // HTML-entity-escaped, min 2 chars after trim
  completed: boolean; // default: false
}

type State = Todo[];  // initial: []
```

**No persistence.** State exists only in React component memory. Page reload clears all data.

## Actions (Reducer)

| Action | Payload | Transition |
|---|---|---|
| `ADD_ITEM` | `{title: string}` | Append `{id: nanoid(), title, completed: false}` |
| `UPDATE_ITEM` | `{id: string, title: string}` | Replace title of todo with matching id |
| `REMOVE_ITEM` | `{id: string}` | Remove todo with matching id |
| `TOGGLE_ITEM` | `{id: string}` | Flip `completed` of todo with matching id |
| `TOGGLE_ALL` | `{completed: boolean}` | Set all todos' `completed` to payload value |
| `REMOVE_COMPLETED_ITEMS` | (none) | Remove all todos where `completed === true` |
| `REMOVE_ALL_ITEMS` | (none) | Replace state with `[]` (not exposed in UI) |

Unknown actions throw `Error("Unknown action: ${type}")`.

## Components & Behavior

### Header

- **Element:** `<header class="header">`
- **Contains:** `<h1>todos</h1>` + Input component
- **Input placeholder:** "What needs to be done?"
- **Input id:** `todo-input` with associated `<label class="visually-hidden">`

### Input (shared component)

Used for both new-todo creation and inline editing.

**Props:** `onSubmit`, `placeholder`, `label`, `defaultValue`, `onBlur`

**Behavior:**
1. `Enter` key triggers submission
2. Value is trimmed (`value.trim()`)
3. Minimum length validation: `value.length >= 2` (after trim)
4. Sanitization: manual HTML entity encoding of `& < > " ' /`
5. On valid submit: calls `onSubmit(sanitizedValue)`, clears input
6. On invalid (< 2 chars): no action, input retains value
7. `autoFocus` attribute set

### Main (todo list)

- **Element:** `<main class="main">`
- **Contains:** toggle-all control + `<ul class="todo-list">`
- **Filtering:** `useMemo` on `useLocation().pathname`:
  - `/` → all todos
  - `/active` → `!todo.completed` only
  - `/completed` → `todo.completed` only
- **Toggle-all:** visible only when `visibleTodos.length > 0`
  - `<input class="toggle-all" type="checkbox" id="toggle-all">`
  - `checked` state: `visibleTodos.every(todo => todo.completed)`
  - `onChange`: dispatches `TOGGLE_ALL` with `e.target.checked`
  - Scoped to visible todos' checked state, but dispatches to ALL todos
  - `<label class="toggle-all-label" for="toggle-all">Toggle All Input</label>`

### Item (single todo)

- **Element:** `<li class="completed?">`  (conditional via classnames)
- **Wrapped in:** `React.memo` for render optimization
- **Two modes:** view mode and edit mode (controlled by local `isWritable` state)

**View mode** (`isWritable === false`):
- `<div class="view">`
  - `<input class="toggle" type="checkbox">` — toggles completed
  - `<label>` — displays title, double-click enters edit mode
  - `<button class="destroy">` — removes item

**Edit mode** (`isWritable === true`):
- Replaces entire `.view` content with Input component
- `defaultValue` set to current title
- `onBlur` exits edit mode (setIsWritable(false))
- `onSubmit`: if title empty → remove item; else → update title, exit edit
- **Note:** Edit mode replaces the `.view` div contents rather than using a separate `.edit` class alongside `.view`. The CSS `.todo-list li.editing` class is defined but the component uses conditional rendering instead.

### Footer

- **Element:** `<footer class="footer">`
- **Visibility:** hidden when `todos.length === 0` (returns null)
- **Todo count:** `<span class="todo-count">{n} item(s) left!</span>`
  - Pluralization: "item" for 1, "items" for 0 or 2+
  - Text includes exclamation mark: "1 item left!" / "2 items left!"
- **Filters:** `<ul class="filters">` with 3 `<li>` containing `<a>` links
  - "All" → `#/`
  - "Active" → `#/active`
  - "Completed" → `#/completed`
  - Selected state: `class="selected"` via classnames on current route match
- **Clear completed:** `<button class="clear-completed">Clear completed</button>`
  - `disabled` when `activeTodos.length === todos.length` (no completed items)
  - Click dispatches `REMOVE_COMPLETED_ITEMS`

## Routing

Hash-based routing via `react-router-dom` HashRouter.

```
#/           → show all todos (default)
#/active     → show active (uncompleted) todos only
#/completed  → show completed todos only
```

Routes are defined as `<Route path="*" element={<App />} />` — single catch-all route. Components read `useLocation().pathname` directly for filter logic.

## Visual Design

### Layout

| Property | Value |
|---|---|
| Body max-width | 550px |
| Body min-width | 230px |
| Body margin | 0 auto (centered) |
| Body background | #f5f5f5 |
| Font stack | Helvetica Neue, Helvetica, Arial, sans-serif |
| Base font size | 14px |
| Base font weight | 300 |
| Base line-height | 1.4em |

### App Container (`.todoapp`)

| Property | Value |
|---|---|
| Background | #fff |
| Margin | 130px 0 40px |
| Position | relative |
| Box-shadow | 0 2px 4px rgba(0,0,0,0.2), 0 25px 50px rgba(0,0,0,0.1) |

### Title (`h1`)

| Property | Value |
|---|---|
| Text | "todos" |
| Color | #b83f45 (muted red) |
| Font size | 80px |
| Font weight | 200 (extra-light) |
| Position | absolute, top: -140px |
| Text align | center, width: 100% |
| Text rendering | optimizeLegibility |

### New Todo Input (`.new-todo`)

| Property | Value |
|---|---|
| Height | 65px |
| Font size | 24px |
| Padding | 16px 16px 16px 60px |
| Background | rgba(0,0,0,0.003) |
| Border | none |
| Box-shadow | inset 0 -2px 1px rgba(0,0,0,0.03) |
| Placeholder style | color rgba(0,0,0,0.4), italic, weight 400 |

### Todo Items (`.todo-list li`)

| Property | Value |
|---|---|
| Font size | 24px |
| Border-bottom | 1px solid #ededed |
| Last child | no border-bottom |
| Position | relative |

**Label** (`.todo-list li label`):
- Color: #484848
- Padding: 15px 15px 15px 60px
- Line-height: 1.2
- Word-break: break-all
- Transition: color 0.4s

**Completed label** (`.todo-list li.completed label`):
- Color: #949494
- Text-decoration: line-through

**Toggle checkbox** (`.todo-list li .toggle`):
- Visually hidden (opacity: 0, positioned absolutely)
- Adjacent label gets SVG background-image:
  - Unchecked: gray circle outline (stroke #949494)
  - Checked: green circle with checkmark (stroke #59A193, fill #3EA390)

**Destroy button** (`.todo-list li .destroy`):
- Hidden by default (`display: none`)
- Shown on parent hover (`li:hover .destroy { display: block }`)
- Content: "×" via `:after` pseudo-element
- Color: #949494, hover: #c18585
- Size: 40x40px, positioned absolute right: 10px

### Edit Mode (`.todo-list li.editing`)

| Property | Value |
|---|---|
| Border-bottom | none |
| `.view` | display: none |
| `.edit` | display: block, margin-left 43px, width calc(100% - 43px) |

### Footer (`.footer`)

| Property | Value |
|---|---|
| Border-top | 1px solid #e6e6e6 |
| Height | 20px |
| Padding | 10px 15px |
| Font size | 15px |
| Text-align | center |
| `:before` pseudo | Stacked paper effect via multiple box-shadows |

**Stacked paper effect** (`footer:before`):
```css
box-shadow: 0 1px 1px rgba(0,0,0,0.2),
            0 8px 0 -3px #f6f6f6,
            0 9px 1px -3px rgba(0,0,0,0.2),
            0 16px 0 -6px #f6f6f6,
            0 17px 2px -6px rgba(0,0,0,0.2);
```

**Filter links** (`.filters li a`):
- Border: 1px solid transparent (default)
- Hover: border-color #db7676
- Selected: border-color #ce4646
- Padding: 3px 7px, margin: 3px
- Border-radius: 3px

**Clear completed**: float right, cursor pointer, underline on hover.

### Focus Styles

Focus ring: `box-shadow: 0 0 2px 2px #cf7d7d; outline: 0` — applied to `.toggle-all:focus+label`, `.toggle:focus+label`, and generic `:focus`.

### Toggle All

- Visually hidden checkbox with adjacent label
- Label displays `❯` rotated 90° (downward chevron)
- Unchecked color: #949494, checked color: #484848
- Label size: 45px wide, 65px tall

### Responsive

- `@media (max-width: 430px)`: footer height 50px, filters positioned bottom: 10px
- `@media (min-width: 899px)`: learn sidebar slides in from left

## Edge Cases

| Scenario | Behavior | Verified |
|---|---|---|
| Empty input + Enter | No action (fails min-length 2) | Yes |
| Single char + Enter | No action (fails min-length 2) | Yes |
| XSS payload `<img onerror>` | Double-escaped: manual sanitize + React JSX escaping | Yes — displays as literal text |
| Edit to empty string | Item removed (via `removeItem`) | Source code |
| All items completed + toggle-all | Unchecks all (checkbox state reflects visible todos) | Yes |
| No items | Footer hidden, toggle-all hidden, empty list | Yes |
| Page reload | All data lost (no persistence) | Yes |
| Unknown action type | Throws `Error("Unknown action: ${type}")` | Source code |
| Rapid add | Each gets unique nanoid, appended in order | Source code |

## Security Properties

1. **XSS prevention:** Double-layered — manual HTML entity escaping in `Input.sanitize()` plus React's built-in JSX text escaping. The manual layer is redundant but defensive.
2. **No eval/innerHTML:** All content rendered through React's virtual DOM.
3. **No external data ingestion:** No API calls, no URL parameter parsing, no postMessage handling.
4. **ID generation:** Non-cryptographic (Math.random). Acceptable for client-only state with no security implications.
5. **No CSRF surface:** No forms submitting to servers.
