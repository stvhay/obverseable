# WindowGlobalActor

```python
from geckordp.actors.targets.window_global import WindowGlobalActor

window = WindowGlobalActor(client, target["actor"])
```

The target IS a WindowGlobalActor.

## Methods

| Method | Returns | Notes |
|---|---|---|
| `list_frames()` | `list` | `{id, url, title, isTopLevel, parentID}` per frame/iframe |
| `list_workers()` | `dict` | `{workers: [...]}` |
| `focus()` | `dict` | Focus the tab |
| `reload()` | `dict` | Reload page |
| `navigate_to(url)` | `dict` | Navigate to URL |
| `go_back()` | `dict` | History back |
| `go_forward()` | `dict` | History forward |
| `log_in_page(text, category, flags)` | `dict` | Log to page console |
| `switch_to_frame(window_id)` | `dict` | Switch to iframe |
| `detach()` | `dict` | |
