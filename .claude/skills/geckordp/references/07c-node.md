# NodeActor & NodeListActor

## NodeActor

```python
from geckordp.actors.node import NodeActor

node = NodeActor(client, body_node["actor"])
```

Created from node objects returned by walker methods.

| Method | Returns | Notes |
|---|---|---|
| `get_unique_selector()` | `str` | e.g. `"body"` |
| `get_css_path()` | `str` | e.g. `"html.aAX body.aAU"` |
| `get_x_path()` | `str` | e.g. `"/html/body"` |
| `get_node_value()` | `str` | Text content for text nodes |
| `set_node_value(value)` | `dict` | |
| `get_event_listener_info()` | `list` | |
| `modify_attributes(modifications)` | `dict` | `[{attributeName, newValue}]` |
| `scroll_into_view()` | `dict` | |
| `get_image_data(max_dim=0)` | `dict` | |
| `get_closest_background_color()` | `str` | Walks ancestor tree |
| `get_background_color()` | `str` | Node's own computed bg |
| `get_owner_global_dimensions()` | `dict` | Viewport/window dimensions |
| `get_font_family_data_url(font, fill_style="")` | `dict` | Font preview |
| `wait_for_frame_load()` | `dict` | Waits for iframe content to load |

## Node Object Structure

```python
{
    "actor": "server1.conn85.child2/domnode28",
    "nodeName": "BODY",
    "nodeType": 1,               # 1=ELEMENT, 3=TEXT, 9=DOCUMENT
    "numChildren": 5,
    "parent": "domnode19",
    "attrs": [{"name": "class", "value": "foo"}],
    "displayType": "block",
    "isScrollable": True,
    "isDisplayed": True,
    "isShadowRoot": False,
    "isShadowHost": False,
    "hasEventListeners": True,
}
```

## NodeListActor

```python
from geckordp.actors.node_list import NodeListActor

nodelist = NodeListActor(client, query_result["actor"])
```

From `query_selector_all()` or `search()`.

| Method | Returns | Notes |
|---|---|---|
| `item(index)` | `dict` | `{node: {...}, newParents: [...]}` |
| `items(start, end)` | `dict` | `{nodes: [...]}` — end exclusive |
| `release()` | `dict` | Free server memory |
