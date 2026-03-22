# ScreenshotActor

**Use root-level actor, NOT target-level.** `target["screenshotContentActor"]` is broken on Firefox 140+.

## Setup

```python
from geckordp.actors.screenshot import ScreenshotActor

root_info = root.get_root()
screenshot = ScreenshotActor(client, root_info["screenshotActor"])
```

## capture()

```python
def capture(
    browsing_context_id,       # from tabs[0]["browsingContextID"]
    fullpage=True,
    file=False,                # save to disk
    copy_clipboard=False,      # copy to system clipboard
    selector="",               # CSS selector to capture
    dpr=2,                     # device pixel ratio
    delay_sec=0,               # delay before capture (seconds)
    snapshot_scale=1,          # scale multiplier (distinct from dpr)
    left=None,                 # rect params — all four must be truthy
    top=None,
    width=None,
    height=None,
)
```

**Returns:** `{value: {data: "data:image/png;base64,..."}}`

**Rect gotcha:** If any of `left`, `top`, `width`, `height` is falsy (including `0`), the rect is silently skipped.

## Usage

```python
import base64

result = screenshot.capture(tabs[0]["browsingContextID"])
data_uri = result["value"]["data"]
b64_data = data_uri.split(",", 1)[1]
img_bytes = base64.b64decode(b64_data)
# img_bytes is valid PNG (starts with \x89PNG)
```
