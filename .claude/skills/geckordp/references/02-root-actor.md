# RootActor

```python
from geckordp.actors.root import RootActor

root = RootActor(client)
```

Actor ID: always `"root"`. Extends ResourceActor.

## Methods

| Method | Returns | Notes |
|---|---|---|
| `list_tabs()` | `list[dict]` | `actor`, `browserId`, `browsingContextID`, `title`, `url`, `selected` |
| `current_tab()` | `dict` | First tab where `selected==true` |
| `get_tab(browser_id)` | `dict` | Specific tab |
| `list_addons()` | `list[dict]` | Installed extensions |
| `list_workers()` | `list[dict]` | Web Workers |
| `list_service_worker_registrations()` | `list[dict]` | Service workers |
| `list_processes()` | `list[dict]` | `id`, `isParent`, `actor` |
| `get_process(pid)` | `dict` | `{processDescriptor: {...}}` |
| `get_root()` | `dict` | Root info with actor IDs |
| `request_types()` | `list[str]` | All supported RDP methods |

## Root-Level Actors (from get_root())

| Key | Actor |
|---|---|
| `preferenceActor` | PreferenceActor |
| `deviceActor` | DeviceActor |
| `screenshotActor` | ScreenshotActor |
| `heapSnapshotFileActor` | HeapSnapshotActor |
| `addonsActor` | AddonsActor |
| `parentAccessibilityActor` | ParentAccessibilityActor |
| `perfActor` | Performance (deprecated) |

## ResourceActor Methods (inherited)

| Method | Notes |
|---|---|
| `watch_resources(resources: list[Resources])` | Start streaming events |
| `unwatch_resources(resources: list[Resources])` | Fire-and-forget (no response) |
| `clear_resources(resources: list[Resources])` | Fire-and-forget |
