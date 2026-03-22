# Connection Setup

## Firefox Prefs (about:config)

Required:

| Pref | Value |
|---|---|
| `devtools.debugger.remote-enabled` | `true` |
| `devtools.debugger.force-local` | `false` |
| `devtools.debugger.prompt-connection` | `false` |
| `devtools.chrome.enabled` | `true` |

Optional (set by `ProfileManager.set_required_configs()`):

| Pref | Value | Purpose |
|---|---|---|
| `devtools.cache.disabled` | `true` | Disable HTTP cache |
| `browser.sessionstore.resume_from_crash` | `false` | Prevent crash recovery |
| `privacy.userContext.enabled` | `true` | Enable container tabs |

Launch: `firefox --start-debugger-server 6000`

## Connection Pattern

```python
from geckordp.rdp_client import RDPClient
from geckordp.actors.root import RootActor
from geckordp.actors.descriptors.tab import TabActor

client = RDPClient(timeout_sec=5.0)
client.connect("192.168.64.1", 6000)

root = RootActor(client)
tabs = root.list_tabs()
tab_actor = TabActor(client, tabs[0]["actor"])
target = tab_actor.get_target()

# target contains all actor IDs:
# consoleActor, inspectorActor, threadActor, networkContentActor,
# memoryActor, accessibilityActor, screenshotContentActor,
# styleSheetsActor, animationsActor, changesActor, tracerActor,
# objectsManagerActor

client.disconnect()
```

## Context Manager

RDPClient supports `with` for automatic cleanup:

```python
with RDPClient(timeout_sec=5.0) as client:
    client.connect("host", 6000)
    # ... work ...
# disconnect() called automatically on exit
```
