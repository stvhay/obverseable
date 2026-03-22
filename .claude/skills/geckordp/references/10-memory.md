# MemoryActor & HeapSnapshotActor

## MemoryActor

```python
from geckordp.actors.memory import MemoryActor

mem = MemoryActor(client, target["memoryActor"])
```

**Must call `attach()` first** for most methods.

| Method | Returns | Notes |
|---|---|---|
| `attach()` | `dict` | Required |
| `detach()` | `dict` | |
| `measure()` | `dict` | Memory measurements in bytes |
| `resident_unique()` | `dict` | |
| `take_census()` | `dict` | Object type breakdown |
| `start_recording_allocations(probability=None, max_log_length=None)` | `dict` | `probability`: 0.0–1.0 sampling rate. `max_log_length`: cap on log size. Both raise `ValueError` if out of range. |
| `get_allocations_settings()` | `dict` | |
| `get_allocations()` | `dict` | |
| `stop_recording_allocations()` | `dict` | |
| `force_garbage_collection()` | `dict` | |
| `force_cycle_collection()` | `dict` | |
| `get_state()` | `dict` | |
| `save_heap_snapshot(boundaries=None)` | `str` | Returns snapshot ID string (not dict). Use with HeapSnapshotActor. |

## HeapSnapshotActor

```python
from geckordp.actors.heap_snapshot import HeapSnapshotActor
```

Access from root: `root.get_root()["heapSnapshotFileActor"]`

| Method | Returns | Notes |
|---|---|---|
| `transfer_heap_snapshot(snapshot_id)` | `dict` | Bulk response: base64-encoded binary heap data |

### Workflow

```python
mem = MemoryActor(client, target["memoryActor"])
mem.attach()
snapshot_id = mem.save_heap_snapshot()

root_info = root.get_root()
heap = HeapSnapshotActor(client, root_info["heapSnapshotFileActor"])
data = heap.transfer_heap_snapshot(snapshot_id)
```
