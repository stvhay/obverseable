# PreferenceActor & DeviceActor

Root-level actors from `root.get_root()`.

## PreferenceActor

```python
from geckordp.actors.preference import PreferenceActor

pref = PreferenceActor(client, root.get_root()["preferenceActor"])
```

| Method | Returns | Notes |
|---|---|---|
| `get_bool_pref(name)` | `dict` | `{value: bool}` |
| `get_char_pref(name)` | `dict` | `{value: str}` |
| `get_int_pref(name)` | `dict` | `{value: int}` |
| `set_bool_pref(name, value)` | `dict` | |
| `set_char_pref(name, value)` | `dict` | |
| `set_int_pref(name, value)` | `dict` | |
| `clear_user_pref(name)` | `dict` | |
| `get_all_prefs(value)` | `dict` | **Note: `value` parameter is required** |
| `get_traits()` | `dict` | Capability probe |

## DeviceActor

```python
from geckordp.actors.device import DeviceActor

device = DeviceActor(client, root.get_root()["deviceActor"])
```

| Method | Returns | Notes |
|---|---|---|
| `get_description()` | `dict` | Browser version, OS, arch, user agent, screen resolution |
