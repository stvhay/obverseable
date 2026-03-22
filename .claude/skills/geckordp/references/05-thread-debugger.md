# ThreadActor (Debugger)

```python
from geckordp.actors.thread import ThreadActor

thread = ThreadActor(client, target["threadActor"])
```

## attach() — Must Call First

```python
def attach(
    pause_on_exceptions=False,
    ignore_caught_exceptions=True,
    should_show_overlay=False,
    should_include_saved_frames=True,
    should_include_async_live_frames=False,
    skip_breakpoints=False,
    log_event_breakpoints=False,
    observe_asm_js=True,
    breakpoints: dict | None = None,       # pre-load breakpoints
    event_breakpoints: list | None = None,  # pre-load event breakpoints
)
```

Pre-loading breakpoints at attach avoids race conditions.

## Core Methods

| Method | Returns | Notes |
|---|---|---|
| `attach(...)` | `dict` | See above |
| `interrupt(when=When.NOW)` | `dict` | Pause execution |
| `resume(resume_limit=ResumeLimit.NONE, frame_actor_id="")` | `dict` | **Error if not paused** |
| `sources()` | `list` | All JS sources |
| `frames(start, count)` | `list` | **Only when paused** |
| `is_attached()` | `bool` | |
| `dump_thread()` | `dict` | `{pauseOnExceptions, breakpoints, ...}` |
| `dump_pools()` | `dict` | Note: response structure incompatible with rdpclient |

## Resume Limits

```python
class ResumeLimit(Enum):
    NONE = None      # Run freely (wire: null)
    STEP = "step"    # Step into
    NEXT = "next"    # Step over
    FINISH = "finish" # Step out
    RESTART = "restart"
    BREAK = "break"  # Run to next breakpoint
```

## When Enum

```python
class When(str, Enum):
    NOW = ""          # Interrupt immediately
    ON_NEXT = "onNext" # On next event loop turn
```

## Breakpoints

| Method | Returns | Notes |
|---|---|---|
| `set_breakpoint(line, column, source_url="", source_id="", condition="", log_value="")` | `dict` | Prefer `source_id` over URL |
| `remove_breakpoint(line, column, source_url="", source_id="")` | `dict` | |
| `set_xhr_breakpoint(path, method="ANY")` | `bool` | |
| `remove_xhr_breakpoint(path, method)` | `bool` | |

## Event Breakpoints

| Method | Returns |
|---|---|
| `get_available_event_breakpoints()` | `list` — 18 categories |
| `get_active_event_breakpoints()` | `list[str]` |
| `set_active_event_breakpoints(ids)` | `dict` |

## Config

| Method | Notes |
|---|---|
| `reconfigure(observe_asm_js=True, pause_workers_until_attach=True, skip_breakpoints=None, log_event_breakpoints=None)` | Note: `skip_breakpoints` is `dict`, `log_event_breakpoints` is `list` (type anomaly) |
| `pause_on_exceptions(pause_on_exceptions, ignore_caught_exceptions)` | Params typed as `str` |
| `toggle_event_logging(log_event_breakpoints)` | |
| `skip_breakpoints(skip_breakpoints=None)` | |
