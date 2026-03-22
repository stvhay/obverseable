# Storage Actors

```python
from geckordp.actors.storage import (
    CookieStorageActor,
    LocalStorageActor,
    SessionStorageActor,
    ExtensionStorageActor,
    CacheStorageActor,
    IndexedDBStorageActor,
)
```

Storage actors provide CRUD access to browser storage. Obtain actor IDs from `resources-available-array` events after watching the appropriate resource type.

## Setup

```python
watcher.watch_resources([Resources.COOKIE])
watcher.watch_resources([Resources.LOCAL_STORAGE])
watcher.watch_resources([Resources.SESSION_STORAGE])
watcher.watch_resources([Resources.INDEXED_DB])
watcher.watch_resources([Resources.CACHE_STORAGE])
```

Actor IDs arrive in the `resources-available-array` event payloads.

## CookieStorageActor

| Method | Returns | Notes |
|---|---|---|
| `get_store_objects(host, names=None, options=None)` | `dict` | List cookies for host |
| `get_fields(sub_type=None)` | `dict` | Field schema |
| `add_item(guid, host)` | `dict` | Create cookie |
| `remove_item(host, name)` | `dict` | Delete cookie |
| `edit_item(host, field, old_value, new_value, cookie_data)` | `dict` | Modify cookie field |
| `remove_all(host, domain=None)` | `dict` | Clear all cookies |
| `remove_all_session_cookies(host, domain=None)` | `dict` | Clear session cookies only |

## LocalStorageActor

| Method | Returns |
|---|---|
| `get_store_objects(host, names=None, options=None)` | `dict` |
| `get_fields(sub_type=None)` | `dict` |
| `add_item(guid, host)` | `dict` |
| `remove_item(host, name)` | `dict` |
| `edit_item(data: dict)` | `dict` |
| `remove_all(host)` | `dict` |

## SessionStorageActor

Same methods as LocalStorageActor.

## ExtensionStorageActor

| Method | Returns |
|---|---|
| `get_store_objects(host, names=None, options=None)` | `dict` |
| `get_fields(sub_type=None)` | `dict` |
| `remove_item(host, name)` | `dict` |
| `edit_item(data: dict)` | `dict` |
| `remove_all(host)` | `dict` |

No `add_item`.

## CacheStorageActor

| Method | Returns | Notes |
|---|---|---|
| `get_store_objects(host, names=None, options=None)` | `dict` | |
| `get_fields(sub_type=None)` | `dict` | |
| `remove_item(host, name)` | `dict` | |
| `remove_all(host, name)` | `dict` | Takes both host AND cache name |

## IndexedDBStorageActor

| Method | Returns | Notes |
|---|---|---|
| `get_store_objects(host, names=None, options=None)` | `dict` | |
| `get_fields(sub_type=None)` | `dict` | |
| `remove_item(host, name)` | `dict` | |
| `remove_database(host, name)` | `dict` | Delete entire database — unique to IndexedDB |
