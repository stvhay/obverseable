# GECKORDP Settings & Debugging

## Runtime Settings

```python
from geckordp.settings import GECKORDP

GECKORDP.DEBUG = 1                  # Enable debug mode
GECKORDP.DEBUG_REQUEST = 1          # Log all sent RDP messages
GECKORDP.DEBUG_RESPONSE = 1         # Log all received RDP messages
GECKORDP.DEBUG_EVENTS = 1           # Log all events
GECKORDP.DEBUG_REQUEST_FORMAT = 1   # Pretty-print requests (default: on)
GECKORDP.DEBUG_RESPONSE_FORMAT = 1  # Pretty-print responses (default: on)
GECKORDP.LOG_FILE = "debug.log"     # Write to file (empty = disabled)
GECKORDP.LOG_LEVEL = "debug"        # debug, info, warn, error, fatal
```

## Environment Variables

Set before import to auto-configure:

| Env var | Type | Effect |
|---|---|---|
| `GECKORDP_DEBUG` | `0/1` | Enable debug mode |
| `GECKORDP_DEBUG_EVENTS` | `0/1` | Log events |
| `GECKORDP_DEBUG_REQUEST` | `0/1` | Log sent messages |
| `GECKORDP_DEBUG_REQUEST_FORMAT` | `0/1` | Pretty-print requests |
| `GECKORDP_DEBUG_RESPONSE` | `0/1` | Log received messages |
| `GECKORDP_DEBUG_RESPONSE_FORMAT` | `0/1` | Pretty-print responses |
| `GECKORDP_LOG_FILE` | `str` | Log file path |
| `GECKORDP_LOG_LEVEL` | `str` | Log level |

## Python Logging Integration

geckordp uses the `"geckordp"` named logger. Attach your own handler:

```python
import logging
logger = logging.getLogger("geckordp")
logger.setLevel(logging.DEBUG)
logger.addHandler(your_handler)
```

## ProfileManager (for reference)

Not needed for connecting to existing Firefox, but documents which prefs `set_required_configs()` sets (~30 prefs including UI suppression, crash recovery, autoplay, telemetry).

```python
from geckordp.profile import ProfileManager
pm = ProfileManager()
profile = pm.get_profile_by_name("default-release")
profile.set_required_configs()  # sets all required prefs
```

## Firefox.start() (for reference)

```python
from geckordp.firefox import Firefox
Firefox.start("https://example.com/", port=6000, profile_name="geckordp", args=["-headless"])
```

Not used by Obverseable (connects to existing instance), but documents the exact CLI invocation.
