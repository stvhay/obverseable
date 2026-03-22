# TargetConfigurationActor & ThreadConfigurationActor

```python
from geckordp.actors.target_configuration import TargetConfigurationActor
from geckordp.actors.thread_configuration import ThreadConfigurationActor
from geckordp.actors.watcher import WatcherActor
```

Both obtained via WatcherActor. These are the modern watcher-based configuration APIs.

## TargetConfigurationActor

```python
watcher_resp = tab_actor.get_watcher()
watcher = WatcherActor(client, watcher_resp["actor"])
config_resp = watcher.get_target_configuration_actor()
config = TargetConfigurationActor(client, config_resp["actor"])
```

### update_configuration()

All parameters are optional. Only non-None/non-sentinel values are sent.

| Parameter | Type | Default | What it controls |
|---|---|---|---|
| `cache_disabled` | `bool \| None` | `None` | Disable HTTP cache |
| `custom_formatters` | `bool \| None` | `None` | Custom object formatters |
| `color_scheme_simulation` | `bool \| None` | `None` | `prefers-color-scheme` simulation |
| `custom_user_agent` | `str` | `""` | Override User-Agent |
| `javascript_enabled` | `bool \| None` | `None` | Enable/disable JS |
| `override_dppx` | `float` | `-1` | Override device pixel ratio |
| `paint_flashing` | `bool \| None` | `None` | Highlight repaint regions |
| `print_simulation_enabled` | `bool \| None` | `None` | Print media query |
| `restore_focus` | `bool \| None` | `None` | Restore focus after picker |
| `service_workers_testing_enabled` | `bool \| None` | `None` | SW testing mode |
| `use_simple_highlighters_for_reduced_motion` | `bool \| None` | `None` | |
| `touch_events_override` | `str` | `""` | Touch event handling |

## ThreadConfigurationActor

Modern alternative to `ThreadActor.reconfigure()`.

```python
thread_config_resp = watcher.get_thread_configuration_actor()
thread_config = ThreadConfigurationActor(client, thread_config_resp["actor"])
```

### update_configuration()

All parameters optional. Only non-None values sent.

| Parameter | Type | What it controls |
|---|---|---|
| `should_pause_on_debugger_statement` | `bool \| None` | Honor `debugger;` statements |
| `pause_on_exceptions` | `bool \| None` | Pause on uncaught exceptions |
| `ignore_caught_exceptions` | `bool \| None` | Skip try/catch |
| `should_include_saved_frames` | `bool \| None` | Async saved frames |
| `should_include_async_live_frames` | `bool \| None` | Async live frames |
| `skip_breakpoints` | `bool \| None` | Disable all breakpoints (correctly typed, unlike ThreadActor.reconfigure) |
| `log_event_breakpoints` | `bool \| None` | Log instead of break |
| `observe_asm_js` | `bool \| None` | asm.js instrumentation |
| `pause_overlay` | `bool \| None` | Show/hide pause overlay |
