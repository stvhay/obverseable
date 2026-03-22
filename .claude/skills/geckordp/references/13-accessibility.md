# Accessibility Actors

## AccessibilityActor

```python
from geckordp.actors.accessibility.accessibility import AccessibilityActor

a11y = AccessibilityActor(client, target["accessibilityActor"])
```

| Method | Returns | Notes |
|---|---|---|
| `bootstrap()` | `dict` | Initialize a11y. Returns `state` field. |
| `get_traits()` | `dict` | `{tabbingOrder: bool}` |
| `get_walker()` | `{actor: "..."}` | AccessibleWalkerActor |
| `get_simulator()` | `{actor: "..."}` | SimulatorActor |

## AccessibleWalkerActor

From `AccessibilityActor.get_walker()["actor"]`.

| Method | Returns | Notes |
|---|---|---|
| `children()` | `list` | Root-level accessible children |
| `get_accessible_for(dom_node_actor)` | `dict` | Bridge DOM → a11y tree |
| `get_ancestry(accessible)` | `list` | Ancestor chain |
| `start_audit(options=None)` | `dict` | Full-page a11y audit |
| `highlight_accessible(accessible, options=None)` | `dict` | Visual highlight |
| `unhighlight()` | `dict` | Remove highlight |
| `cancel_pick()` | `dict` | |
| `pick_and_focus()` | `dict` | A11y element picker |
| `show_tabbing_order(dom_node_actor, index)` | `dict` | Visualize tab order |

**Gotcha:** `children()`, `get_accessible_for()`, and `start_audit()` tend to timeout without proper a11y context setup. Simple state methods (`pick_and_focus`, `cancel_pick`, `unhighlight`) are reliable.

## AccessibleActor

From walker results (e.g. `get_accessible_for()` response).

| Method | Returns | Notes |
|---|---|---|
| `audit(options=None)` | `dict` | Per-node a11y audit |
| `children()` | `list` | Accessible children |
| `get_relations()` | `list` | ARIA relationships |
| `hydrate()` | `dict` | Full property set |
| `snapshot()` | `dict` | Serialized subtree snapshot |

## ParentAccessibilityActor

From root: `root.get_root()["parentAccessibilityActor"]`. Controls browser-wide a11y engine.

| Method | Returns |
|---|---|
| `bootstrap()` | `dict` |
| `enable()` | `dict` |
| `disable()` | `dict` |

## SimulatorActor

From `AccessibilityActor.get_simulator()["actor"]`.

```python
class Types(str, Enum):
    NONE = "NONE"
    PROTANOPIA = "PROTANOPIA"        # Red color blindness
    DEUTERANOPIA = "DEUTERANOPIA"    # Green color blindness
    TRITANOPIA = "TRITANOPIA"        # Blue color blindness
    ACHROMATOPSIA = "ACHROMATOPSIA"  # Total color blindness
    CONTRAST_LOSS = "CONTRAST_LOSS"
```

| Method | Returns | Notes |
|---|---|---|
| `simulate(simulate_matrix=Types.NONE)` | `{value: bool}` | Sends `[matrix.value]` or `[]` for NONE |
