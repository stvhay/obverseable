# TodoMVC React — Reverse Engineering Case Study

## Target

TodoMVC React implementation at `https://todomvc.com/examples/react/dist/`

## Techniques Used

### 1. Automated Phase 0-2 Recon (`phase_recon.py`)

Single script handling navigation, fingerprinting, script classification, source map extraction, CSS source fetching, style extraction, and network capture. Recovered 28 source files from Webpack source map, plus `base.js` (raw bundle, no source map) and `app.css`.

**Cost:** 1 tool call, ~30 seconds
**Yield:** Complete source tree, surface metadata, network trace, computed styles

### 2. Behavioral Probing (`phase_behavioral.py`)

Async Promise-based probe script testing all interactions with 100ms setTimeout delays between steps for React re-render. Used native input setter pattern for React controlled inputs.

**Verified behaviors:**
- Add (2 items), toggle, filter (All/Active/Completed), toggle-all, clear-completed, XSS escaping
- Edit mode detection (partial — double-click triggers `isWritable` state but probe detected `editingWorks: false` because the component replaces `.view` content with Input component rather than adding `.editing` class to `<li>`)

**Cost:** 1 tool call, ~5 seconds

### 3. Source Code Analysis

Direct reading of recovered source files (9 application files). Architecture derived from import graph and component structure. Key findings:
- `useReducer` (not Redux/Context) for state management
- Embedded nanoid v3 for ID generation
- Manual HTML sanitization redundant with React's built-in escaping
- `REMOVE_ALL_ITEMS` action defined but never dispatched from UI

### 4. CSS Mechanism Analysis

Fetched raw CSS source (not just computed values) to document implementation mechanisms:
- Toggle checkbox uses SVG data URIs in `background-image` on adjacent label
- Destroy button revealed via `:hover` on parent `<li>`
- Footer stacked-paper effect via multiple `box-shadow` layers on `:before` pseudo-element
- Focus styles use `box-shadow` replacement for outline

### 5. Shared Infrastructure Analysis

`base.js` analyzed despite being classified as shared-infra (not app code):
- TodoMVC learn sidebar with micro-template engine
- Google Analytics injection (conditional on hostname)
- `learn.json` fetch for framework metadata
- Legacy domain redirect

## Findings

### Architecture
- 9 source files, clean separation: 1 entry, 1 root component, 5 sub-components, 1 reducer, 1 constants
- React function components throughout — no class components
- Memoization strategy: `React.memo` on Item, `useMemo` for filtered/counted lists, `useCallback` for all handlers
- Hash routing via react-router-dom (not custom)

### Non-obvious
- The `sanitize()` function in `input.jsx` is defense-in-depth but redundant — React already escapes text content in JSX. The double-encoding means stored titles contain entities like `&amp;` which React then renders correctly.
- `REMOVE_ALL_ITEMS` action exists in constants and reducer but is never dispatched by any component. Dead code or future feature.
- Toggle-all checkbox `checked` state is computed from `visibleTodos` (filtered), but the dispatch targets ALL todos. This means toggling on the "Active" filter completes all todos, not just visible ones.
- Edit mode doesn't use the CSS `.editing` class on `<li>`. Instead, the Item component conditionally renders either the `.view` div contents or the Input component. The CSS rules for `.todo-list li.editing` are present in the stylesheet but unused by this implementation.
- No persistence mechanism — unusual for a TodoMVC implementation. Most use `localStorage`.

### Behavioral Probe Gap
The probe reported `editingWorks: false` because it checked for `.todo-list li.editing` class. This React implementation uses conditional rendering instead of class-based toggling. The edit functionality works correctly but detection requires checking for the Input component within `.view` after double-click, not for a CSS class.

## Operational Notes

- `phase_recon.py` handles the entire recon pipeline end-to-end. For TodoMVC-style SPAs, this is the correct starting point.
- `phase_behavioral.py` probe script assumes TodoMVC DOM conventions (`.new-todo`, `.toggle`, `.destroy`, `.filters a`). Works well for standard implementations.
- Edit mode detection in behavioral probe needs to also check for Input component within `.view` (not just `.editing` class) to handle implementations that use conditional rendering.
- Computed styles from empty-page recon missed todo-item selectors (`.todo-list li` etc. returned `found: false`). The behavioral probe's populated style extraction (run after adding items) captured these correctly.
- Network capture returned URLs but metadata (status, mimeType, size) was null for most requests — likely due to stale actor references after reload.
