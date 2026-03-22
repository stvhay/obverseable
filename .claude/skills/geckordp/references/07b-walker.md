# WalkerActor

```python
from geckordp.actors.inspector import InspectorActor
from geckordp.actors.walker import WalkerActor

inspector = InspectorActor(client, target["inspectorActor"])
walker = WalkerActor(client, inspector.get_walker()["actor"])
```

## Traversal

| Method | Returns | Notes |
|---|---|---|
| `document()` | `dict` | Root `#document` node |
| `document_element(dom_node_actor)` | `dict` | `<html>` element (distinct from document) |
| `children(node_actor, max_nodes=1000, center_node="", start_node="", what_to_show="")` | `list` | Direct children |
| `next_sibling(node_actor, what_to_show="")` | `dict \| null` | |
| `previous_sibling(node_actor, what_to_show="")` | `dict \| null` | |

## Query

| Method | Returns | Notes |
|---|---|---|
| `query_selector(node_actor, selector)` | `dict` | `{node: {...}, newParents: [...]}` — access `['node']` |
| `query_selector_all(node_actor, selector)` | `dict` | `{actor: "NodeListID", length: N}` |
| `search(query)` | `dict` | `{list: {actor, length}, metadata: [...]}` |
| `get_suggestions_for_query(completing, query="", selector_state="tag")` | `dict` | CSS selector autocomplete |

## HTML Manipulation

| Method | Returns | Notes |
|---|---|---|
| `inner_html(node_actor)` | LongString | `{type: "longString", actor: "...", length: N, initial: "..."}`. See `17-string-actor.md` for paging. |
| `outer_html(node_actor)` | LongString | Same shape |
| `set_inner_html(node_actor, value)` | `dict` | |
| `set_outer_html(node_actor, value)` | `dict` | |
| `insert_adjacent_html(node_actor, position, value)` | `dict` | Position enum below |
| `remove_node(node_actor)` | `dict` | |
| `remove_nodes(dom_node_actors: list[str])` | `dict` | Batch remove |
| `duplicate_node(node_actor)` | `dict` | |
| `edit_tag_name(node_actor, tag_name)` | `dict` | |
| `insert_before(node_actor, parent_actor, sibling_actor="")` | `dict` | DOM reparenting |

## Element Picker

| Method | Returns | Notes |
|---|---|---|
| `pick(focus, is_local_tab)` | `dict` | Activates element picker |
| `cancel_pick()` | `dict` | Cancels picker |
| `clear_picker()` | — | Fire-and-forget |

## State & Mutations

| Method | Returns |
|---|---|
| `get_mutations(cleanup)` | `list[dict]` |
| `is_in_dom_tree(node_actor)` | `dict` |
| `set_mutation_breakpoints(node_actor, subtree, removal, attribute)` | `dict` — DOM mutation breakpoints |
| `add_pseudo_class_lock(node, pseudo_class, parents)` | `dict` |
| `remove_pseudo_class_lock(node, pseudo_class, parents)` | `dict` |
| `clear_pseudo_class_locks(node)` | `dict` |
| `retain_node(node_actor)` | `dict` |
| `unretain_node(node_actor)` | `dict` |
| `release_node(node_actor)` | `dict` — free server memory for specific node |
| `release()` | `dict` — free entire walker |
| `watch_root_node()` | `dict` — subscribe to root node changes (navigation) |

## Cross-Context Resolution

| Method | Returns |
|---|---|
| `get_node_actor_from_window_id(window_id)` | `dict` |
| `get_node_actor_from_content_dom_reference(ref)` | `dict` |
| `get_style_sheet_owner_node(style_sheet_actor_id)` | `dict` |
| `get_node_from_actor(actor_id, paths=None)` | `dict` |
| `get_embedder_element(browsing_context_id)` | `dict` — iframe element |

## Layout

| Method | Returns |
|---|---|
| `get_layout_inspector()` | `dict` |
| `get_parent_grid_node(node_actor)` | `dict` |
| `get_offset_parent(node_actor)` | `dict` |
| `get_scrollable_ancestor_node(node_actor)` | `dict` |
| `get_overflow_causing_elements(node_actor)` | `dict` |
| `hide_node(node_actor)` | `dict` |
| `unhide_node(node_actor)` | `dict` |

## Enums

```python
class Position(str, Enum):
    BEFORE_BEGIN = "beforeBegin"
    AFTER_BEGIN = "afterBegin"
    BEFORE_END = "beforeEnd"
    AFTER_END = "afterEnd"

class PseudoClass(str, Enum):
    HOVER = ":hover"
    ACTIVE = ":active"
    FOCUS = ":focus"
    FOCUS_VISIBLE = ":focus-visible"
    FOCUS_WITHIN = ":focus-within"
    VISITED = ":visited"
    TARGET = ":target"
```
