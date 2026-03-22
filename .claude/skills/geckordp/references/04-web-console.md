# WebConsoleActor

```python
from geckordp.actors.web_console import WebConsoleActor

console = WebConsoleActor(client, target["consoleActor"])
```

## evaluate_js_async — Two-Stage Async Pattern

Returns `resultID` immediately. Actual result arrives via actor listener.

```python
def evaluate_js_async(
    text: str,
    eager=False,                    # no side effects (for watch expressions)
    frame_actor="",                 # eval in specific stack frame (when paused)
    selected_node_actor="",         # sets $0 to this DOM node
    selected_object_actor="",       # object scope context
    inner_window_id=-1,             # target specific iframe
    mapped: dict | None = None,     # source map hints
)
```

### Usage Pattern

```python
results = []
def on_result(data):
    results.append(data)

client.add_actor_listener(target["consoleActor"], on_result)
console.evaluate_js_async("document.title")
time.sleep(0.5)
client.remove_actor_listener(target["consoleActor"], on_result)

# results[0] = {'resultID': '...', 'from': '...'}              ← stage 1
# results[1] = {'type': 'evaluationResult',                     ← stage 2
#               'resultID': '...',
#               'hasException': False,
#               'input': 'document.title',
#               'result': 'Page Title',
#               'startTime': ..., 'timestamp': ...}
```

### Error Result

```python
{'type': 'evaluationResult', 'hasException': True,
 'result': {'type': 'object', 'class': 'Error', ...},
 'exceptionMessage': 'Error: boom'}
```

### Key Parameters

- **`frame_actor`** — Critical when paused at breakpoint. Without it, eval runs in global scope.
- **`eager`** — Safe watch expressions. Firefox refuses side-effectful expressions.
- **`inner_window_id`** — Required for multi-frame pages (iframes).

## Other Methods

| Method | Returns | Notes |
|---|---|---|
| `get_cached_messages(types: list[MessageTypes])` | `dict` | `{messages: [...]}`. Types: `CONSOLE_API`, `PAGE_ERROR` |
| `start_listeners(listeners: list[Listeners])` | `dict` | |
| `stop_listeners(listeners: list[Listeners])` | `dict` | |
| `autocomplete(text, cursor=0, frame_actor="", selected_node_actor="", authorized_evaluations_json=None, expression_vars_json=None)` | `dict` | |
| `clear_messages_cache()` | — | Fire-and-forget via `send()` |

## Enums

```python
class Listeners(str, Enum):
    PAGE_ERROR = "PageError"
    CONSOLE_API = "ConsoleAPI"
    FILE_ACTIVITY = "FileActivity"
    REFLOW_ACTIVITY = "ReflowActivity"
    DOCUMENT_EVENTS = "DocumentEvents"

class MessageTypes(str, Enum):
    PAGE_ERROR = "PageError"
    CONSOLE_API = "ConsoleAPI"
```
