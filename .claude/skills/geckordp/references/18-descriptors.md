# Descriptor Actors

## ProcessActor

From `root.list_processes()` or `root.get_process(pid)`.

```python
from geckordp.actors.descriptors.process import ProcessActor
proc = ProcessActor(client, process_entry["actor"])
```

| Method | Returns | Notes |
|---|---|---|
| `get_target(is_browser_toolbox_fission=None)` | `dict` | Content process target |
| `get_watcher()` | `dict` | Process-level watcher |

## WorkerActor

From `root.list_workers()` or `window_global.list_workers()`.

```python
from geckordp.actors.descriptors.worker import WorkerActor
worker = WorkerActor(client, worker_entry["actor"])
```

| Method | Returns | Notes |
|---|---|---|
| `detach()` | — | Fire-and-forget |
| `get_target()` | `dict` | Worker target |

## WebExtensionActor

From `root.list_addons()`.

```python
from geckordp.actors.descriptors.web_extension import WebExtensionActor
ext = WebExtensionActor(client, addon_entry["actor"])
```

| Method | Returns |
|---|---|
| `reload()` | `dict` |
| `connect()` | `dict` |
| `get_target()` | `dict` |

## AddonsActor

From root: `root.get_root()["addonsActor"]`.

```python
from geckordp.actors.addon.addons import AddonsActor
addons = AddonsActor(client, root.get_root()["addonsActor"])
```

| Method | Returns | Notes |
|---|---|---|
| `install_temporary_addon(addon_path)` | `dict` | Install extension by filesystem path |

## ContentProcessActor

From process descriptor targets.

| Method | Returns |
|---|---|
| `list_workers()` | `list` |
| `pause_matching_service_workers(origin="")` | `dict` |

## WebExtensionInspectedWindowActor

Available from target as `target["webExtensionInspectedWindowActor"]`. Used by extension DevTools panels.

| Method | Returns | Notes |
|---|---|---|
| `reload(url, line, addon_id, ignore_cache=False, user_agent="", injected_script="")` | `dict` | Reload with extension context |
| `eval(expression, url, line, addon_id)` | `dict` | Eval in extension context |
