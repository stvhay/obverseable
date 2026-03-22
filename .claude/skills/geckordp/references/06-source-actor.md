# SourceActor

```python
from geckordp.actors.source import SourceActor

source = SourceActor(client, source_entry["actor"])
```

Created from source objects returned by `thread.sources()`.

## Methods

| Method | Returns | Notes |
|---|---|---|
| `source()` | `dict` | `{source: "...code...", contentType: "text/javascript"}` |
| `get_breakable_lines()` | `dict` | `{lines: [1, 3, 5, ...]}` |
| `get_breakpoint_positions(start_line=0, start_column=0, end_line=10**10, end_column=10**10)` | `dict` | Valid breakpoint locations |
| `get_breakpoint_positions_compressed(start_line=0, start_column=0, end_line=10**10, end_column=10**10)` | `dict` | Compressed format — more efficient for large sources |
| `set_pause_point(line, column, breakpoint_=True, stepover=True)` | `dict` | Single pause point |
| `set_pause_points(pause_points=None)` | `dict` | Batch: `[{location: {line, column}, types: {breakpoint, stepOver}}]` |
| `blackbox(start_line, start_column, end_line, end_column)` | `dict` | `{pausedInSource: bool}`. All params required. |
| `unblackbox(start_line, start_column, end_line, end_column)` | `dict` | All params required. Wire key: `"ranges"` (vs `"range"` for blackbox) |

## Gotcha

`get_breakpoint_positions()` returns `unrecognizedPacketType` for non-script sources (eval'd code without debuggable source).
