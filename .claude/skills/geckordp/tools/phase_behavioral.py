"""
Phase 4: Behavioral probing for TodoMVC-style apps.

Single script that adds items, tests all interactions with async delays,
extracts populated styles, and returns combined results.

Usage:
    uv run python .claude/skills/geckordp/tools/phase_behavioral.py <target_dir>

Assumes Firefox is already on the target page.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recon import RDPSession, write_json


# Combined behavioral probe + style extraction.
# Uses setTimeout chains to allow framework re-renders between operations.
PROBE_SCRIPT = """
new Promise(resolve => {
    const results = {};
    const steps = [];

    function step(fn) { steps.push(fn); }
    function run(i) {
        if (i >= steps.length) return resolve(JSON.stringify(results));
        steps[i]();
        setTimeout(() => run(i + 1), 100);
    }

    // Helper to set React/Vue controlled input values
    function setInput(input, value) {
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        if (setter) setter.call(input, value);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    // 1. Initial state
    step(() => {
        results.hasApp = !!document.querySelector('.todoapp');
        results.initialTodos = document.querySelectorAll('.todo-list li').length;
        results.hasInput = !!document.querySelector('.new-todo');
        results.inputPlaceholder = document.querySelector('.new-todo')?.placeholder;
    });

    // 2. Add first todo
    step(() => {
        const input = document.querySelector('.new-todo');
        if (input) {
            setInput(input, 'Probe Item Alpha');
            input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
        }
    });
    step(() => {
        results.afterAdd1 = document.querySelectorAll('.todo-list li').length;
    });

    // 3. Add second todo
    step(() => {
        const input = document.querySelector('.new-todo');
        if (input) {
            setInput(input, 'Probe Item Beta');
            input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
        }
    });
    step(() => {
        results.afterAdd2 = document.querySelectorAll('.todo-list li').length;
    });

    // 4. Toggle first todo
    step(() => {
        const toggle = document.querySelector('.todo-list li .toggle');
        if (toggle) toggle.click();
    });
    step(() => {
        const first = document.querySelector('.todo-list li');
        results.firstCompleted = first ? first.classList.contains('completed') : null;
        results.todoCount = document.querySelector('.todo-count')?.textContent;
    });

    // 5. Check footer and filters
    step(() => {
        results.hasFooter = !!document.querySelector('.footer');
        const filters = [...document.querySelectorAll('.filters a')];
        results.filterLinks = filters.map(a => ({
            text: a.textContent.trim(),
            href: a.getAttribute('href'),
            selected: a.classList.contains('selected')
        }));
    });

    // 6. Test Active filter
    step(() => {
        const active = [...document.querySelectorAll('.filters a')].find(a => a.textContent.trim() === 'Active');
        if (active) active.click();
    });
    step(() => {
        results.activeFilterCount = document.querySelectorAll('.todo-list li').length;
    });

    // 7. Test Completed filter
    step(() => {
        const completed = [...document.querySelectorAll('.filters a')].find(a => a.textContent.trim() === 'Completed');
        if (completed) completed.click();
    });
    step(() => {
        results.completedFilterCount = document.querySelectorAll('.todo-list li').length;
    });

    // 8. Back to All
    step(() => {
        const all = [...document.querySelectorAll('.filters a')].find(a => a.textContent.trim() === 'All');
        if (all) all.click();
    });
    step(() => {
        results.allFilterCount = document.querySelectorAll('.todo-list li').length;
    });

    // 9. Double-click to edit
    step(() => {
        const label = document.querySelector('.todo-list li label');
        if (label) label.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
    });
    step(() => {
        results.editingWorks = !!document.querySelector('.todo-list li.editing') ||
                               !!document.querySelector('.todo-list li .edit');
        const editInput = document.querySelector('.todo-list li.editing .edit') ||
                         document.querySelector('.todo-list li input.edit') ||
                         document.querySelector('.todo-list li input[type="text"]:not(.new-todo)');
        results.editInputValue = editInput?.value;
        // Escape to cancel
        if (editInput) {
            editInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', keyCode: 27, bubbles: true }));
        }
    });

    // 10. Clear completed
    step(() => {
        const btn = document.querySelector('.clear-completed');
        results.hasClearCompleted = !!btn;
        results.clearCompletedText = btn?.textContent;
        results.clearCompletedDisabled = btn?.disabled;
    });

    // 11. Toggle all
    step(() => {
        const toggleAll = document.querySelector('.toggle-all') || document.querySelector('#toggle-all');
        if (toggleAll) toggleAll.click();
    });
    step(() => {
        results.allCompletedAfterToggleAll = [...document.querySelectorAll('.todo-list li')]
            .every(li => li.classList.contains('completed'));
    });

    // 12. Clear completed
    step(() => {
        const btn = document.querySelector('.clear-completed');
        if (btn && !btn.disabled) btn.click();
    });
    step(() => {
        results.afterClearCompleted = document.querySelectorAll('.todo-list li').length;
    });

    // 13. Edge cases: XSS, empty, single char
    step(() => {
        const input = document.querySelector('.new-todo');
        if (input) {
            setInput(input, '<img src=x onerror=alert(1)>');
            input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
        }
    });
    step(() => {
        const label = document.querySelector('.todo-list li label');
        results.xssEscaped = label ? !label.innerHTML.includes('<img') : null;
        results.xssText = label?.textContent?.slice(0, 50);
    });

    // 14. Persistence check
    step(() => {
        results.localStorageKeys = Object.keys(localStorage);
        for (const key of Object.keys(localStorage)) {
            try {
                const val = JSON.parse(localStorage.getItem(key));
                if (Array.isArray(val)) {
                    results.persistence = { key, count: val.length };
                    break;
                }
            } catch(e) {}
        }
        results.hashRouting = location.hash;
    });

    // 15. Extract populated styles
    step(() => {
        const sels = [
            '.todo-list li', '.todo-list li label', '.todo-list li .toggle',
            '.todo-list li .destroy', '.todo-list li.completed label',
            '.footer', '.todo-count', '.filters li a', '.filters li a.selected',
            '.clear-completed', '.toggle-all', '.view', '.edit'
        ];
        results.populatedStyles = sels.map(sel => {
            const el = document.querySelector(sel);
            if (!el) return {selector: sel, found: false};
            const cs = getComputedStyle(el);
            return {
                selector: sel, found: true, tag: el.tagName,
                color: cs.color, backgroundColor: cs.backgroundColor,
                fontFamily: cs.fontFamily, fontSize: cs.fontSize,
                fontWeight: cs.fontWeight, lineHeight: cs.lineHeight,
                padding: cs.padding, margin: cs.margin,
                border: cs.border, borderRadius: cs.borderRadius,
                textDecoration: cs.textDecoration, cursor: cs.cursor
            };
        });
    });

    run(0);
})
"""


def run(target_dir, prefix=""):
    """Run behavioral probe on current page. Returns probe results dict."""
    pfx = f"{prefix}_" if prefix else ""

    with RDPSession() as s:
        # Stash the async result
        s.eval_js(
            f"({PROBE_SCRIPT}).then(r => {{ window.__probe_result = r }})",
            wait=5.0,
        )
        raw = s.eval_js("window.__probe_result", wait=1.0)
        raw = s._resolve_long_string(raw)
        s.eval_js("delete window.__probe_result", 0.1)

        if isinstance(raw, str):
            results = json.loads(raw)
        else:
            results = raw or {}

        write_json(results, os.path.join(target_dir, f"notes/{pfx}behavioral_probe.json"))

        # Extract populated styles separately if not in results
        if "populatedStyles" in results:
            write_json(
                results["populatedStyles"],
                os.path.join(target_dir, f"notes/{pfx}styles_populated.json"),
            )

        print(f"[probe] Behavioral probe complete")
        for k, v in results.items():
            if k != "populatedStyles":
                print(f"  {k}: {v}")

        return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: phase_behavioral.py <target_dir> [prefix]")
        sys.exit(1)
    target_dir = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""
    run(target_dir, prefix)
