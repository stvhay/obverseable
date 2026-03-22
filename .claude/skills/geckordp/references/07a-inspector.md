# InspectorActor

```python
from geckordp.actors.inspector import InspectorActor

inspector = InspectorActor(client, target["inspectorActor"])
```

## Methods

| Method | Returns | Notes |
|---|---|---|
| `get_walker(options_json=None)` | `dict` | `{actor: "...", root: {#document node}}` |
| `get_page_style()` | `dict` | Computed styles actor |
| `get_compatibility()` | `dict` | Browser compat info |
| `supports_highlighters()` | `dict` | `{value: bool}` |
| `get_highlighter_by_type(type)` | `dict` | See Highlighters enum below |
| `get_image_data_from_url(url, max_dim=0)` | `dict` | Fetch image data from URL |
| `resolve_relative_url(url, dom_node_actor)` | `dict` | Resolve relative URL |
| `pick_color_from_page(options_json)` | `dict` | Eyedropper tool |
| `cancel_pick_color_from_page()` | `dict` | Cancel eyedropper |

## Highlighters Enum

```python
class Highlighters(str, Enum):
    CSS_GRID_HIGHLIGHTER = "CssGridHighlighter"
    BOX_MODEL_HIGHLIGHTER = "BoxModelHighlighter"
    CSS_TRANSFORM_HIGHLIGHTER = "CssTransformHighlighter"
    FLEXBOX_HIGHLIGHTER = "FlexboxHighlighter"
    FONTS_HIGHLIGHTER = "FontsHighlighter"
    GEOMETRY_EDITOR_HIGHLIGHTER = "GeometryEditorHighlighter"
    MEASURING_TOOL_HIGHLIGHTER = "MeasuringToolHighlighter"
    PAUSED_DEBUGGER_OVERLAY = "PausedDebuggerOverlay"
    RULERS_HIGHLIGHTER = "RulersHighlighter"
    SELECTOR_HIGHLIGHTER = "SelectorHighlighter"
    SHAPES_HIGHLIGHTER = "ShapesHighlighter"
```
