# TodoMVC Reverse Engineering — Session Report

## Target

**URL:** https://todomvc.com
**Scope:** Landing page + React implementation (`/examples/react/dist/`) + Vue cross-comparison
**Date:** 2026-03-22

## Techniques Used

### 1. Automated Phase Recon (`phase_recon.py`)

**When:** First contact with target.
**Cost:** 1 tool call, ~30s per URL.
**Result:** Fingerprint, script classification, source map extraction, style extraction, network capture.

**Gotcha:** Network capture hangs when `getEventTimings` is called on stale actor IDs after page reload. The `capture_network(action="reload")` method creates actor IDs from pre-reload context, but they're invalid post-reload. Skipped network detail extraction for this session.

### 2. Source Map Recovery

**When:** After script classification identifies app bundles.
**Cost:** 1 `extract_source_map()` call per bundle, ~5s each.
**Result:** 28 source files recovered from React's webpack bundle. Vue's Vite build had no source maps (production default).

**Technique:** In-browser source map parsing via `fetch(mapUrl).then(r=>r.text()).then(t=>{window.__sm_data=JSON.parse(t)})`. Avoids transferring large maps to Python.

### 3. Single-Script Behavioral Probing

**When:** After source recovery, to validate architecture hypotheses.
**Cost:** 1 eval call, ~2s.
**Result:** 19 behavioral checks in one script: add, toggle, filter, edit (dblclick), delete, toggle-all, clear-completed, XSS, empty input, localStorage, hash routing.

**Technique:** React synthetic event system requires `nativeInputValueSetter` to set controlled input values:
```javascript
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(input, 'text');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

**Gotcha:** Synchronous probing can't observe React re-renders between operations. Some filter counts were incorrect because the DOM hadn't updated between sequential operations. For React apps, use async probing with `setTimeout` delays or `requestAnimationFrame`.

### 4. Computed Style Extraction

**When:** After page has representative content.
**Cost:** 1 `extract_styles()` call per selector set.
**Result:** Key design values (colors, fonts, dimensions, shadows) for body, app container, header, input, info footer.

**Gotcha:** Must extract styles AFTER adding content — selectors like `.todo-list li` return `found: false` when the list is empty. Extract styles with populated state.

### 5. Subagent-Parallel Cross-Implementation Recon

**When:** After primary target analysis is complete.
**Cost:** 1 haiku subagent, ~30s.
**Result:** Vue fingerprint, script classification, styles — enough for comparison table.

**Technique:** Dispatch haiku subagent for data extraction, opus for analysis. Subagent writes to files, main context reads results.

### 6. DOM Tree Walking

**When:** To verify component structure matches source analysis.
**Cost:** 1 `eval_json` call with recursive DOM walker.
**Result:** Full component tree from `section.todoapp` confirming: header > (h1 + input-container), main > (toggle-all-container + todo-list > li > view > (toggle + label + destroy)), footer > (todo-count + filters + clear-completed).

## Key Findings

### Architecture

- **Unidirectional data flow:** App → useReducer → dispatch → pure reducer → new state
- **7 action types** covering full CRUD + batch operations
- **No persistence** — unusual for a todo app reference implementation
- **Client-side HTML sanitization** in Input component, redundant with React's JSX escaping but defense-in-depth
- **nanoid** for IDs — non-cryptographic, inlined from external package

### Shared Infrastructure

- `base.js` is loaded by ALL implementations, providing learn sidebar, analytics, and issue tracking
- Uses vendored Underscore.js template engine
- Conditional analytics (only on todomvc.com hostname)
- Fetches `learn.json` for framework metadata

### Cross-Implementation Patterns

- All implementations share: class names, CSS, hash routing scheme, base.js
- React uses webpack (classic scripts), Vue uses Vite (ES modules)
- Vue detectable via `__VUE__` global, React NOT detectable via standard hooks (devtools hook absent in prod)

## Operational Notes

- **Firefox RDP connection:** 192.168.64.1:6000
- **Network capture bug:** `capture_network(action="reload")` causes 10s timeout per request on `getEventTimings`. Root cause: actor IDs collected during reload reference pre-reload context. Fix needed in `recon.py`.
- **React event simulation:** Native value setter required for controlled inputs. Standard `input.value = x` doesn't trigger React's synthetic event system.
- **Style extraction timing:** Extract styles with content present, not on empty page.
