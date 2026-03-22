# TabActor

```python
from geckordp.actors.descriptors.tab import TabActor

tab_actor = TabActor(client, tab["actor"])
```

## Methods

| Method | Returns | Notes |
|---|---|---|
| `get_target()` | `dict` | All actor IDs for this tab |
| `get_favicon()` | `dict` | `{favicon: "data:..." \| null}` |
| `get_watcher(is_server_target_switching_enabled=True, is_popup_debugging_enabled=False)` | `dict` | `{actor: "watcher_id"}` |

## Target Actor IDs (from get_target())

```
consoleActor, inspectorActor, threadActor, networkContentActor,
memoryActor, accessibilityActor, screenshotContentActor,
styleSheetsActor, animationsActor, changesActor, tracerActor,
objectsManagerActor, reflowActor, cssPropertiesActor,
responsiveActor, manifestActor
```

Plus page info: `title`, `url`, `browsingContextID`, `processID`, `innerWindowId`, `traits`.
