# Network Actors

## Setup — WatcherActor Required First

```python
from geckordp.actors.watcher import WatcherActor
from geckordp.actors.network_parent import NetworkParentActor
from geckordp.actors.network_event import NetworkEventActor
from geckordp.actors.resources import Resources

watcher_resp = tab_actor.get_watcher()
watcher = WatcherActor(client, watcher_resp["actor"])
watcher.watch_resources([Resources.NETWORK_EVENT])

net_parent_resp = watcher.get_network_parent_actor()
net_parent = NetworkParentActor(client, net_parent_resp["network"]["actor"])
```

## WatcherActor

| Method | Returns | Notes |
|---|---|---|
| `watch_resources(resources)` | `dict` | **Must call first** |
| `unwatch_resources(resources)` | — | Fire-and-forget |
| `clear_resources(resources)` | — | Fire-and-forget |
| `watch_targets(target_type)` | `dict` | Targets: FRAME, PROCESS, WORKER |
| `unwatch_targets(target_type)` | — | Fire-and-forget |
| `get_network_parent_actor()` | `dict` | `{network: {actor: "..."}}` |
| `get_parent_browsing_context_id(ctx_id)` | `dict` | iframe hierarchy traversal |
| `get_blackboxing_actor()` | `dict` | |
| `get_breakpoint_list_actor()` | `dict` | |
| `get_target_configuration_actor()` | `dict` | Returns `configuration` sub-object |
| `get_thread_configuration_actor()` | `dict` | Returns `configuration` sub-object |

### Resources Enum (wire values)

```python
NETWORK_EVENT = "network-event"
NETWORK_EVENT_STACKTRACE = "network-event-stacktrace"
CONSOLE_MESSAGE = "console-message"
ERROR_MESSAGE = "error-message"
STYLESHEET = "stylesheet"
CSS_MESSAGE = "css-message"
CSS_CHANGE = "css-change"
DOCUMENT_EVENT = "document-event"
PLATFORM_MESSAGE = "platform-message"
SOURCE = "source"
THREAD_STATE = "thread-state"
SERVER_SENT_EVENT = "server-sent-event"
WEBSOCKET = "websocket"
COOKIE = "cookies"              # NOTE: plural
LOCAL_STORAGE = "local-storage"
SESSION_STORAGE = "session-storage"
INDEXED_DB = "indexed-db"
CACHE_STORAGE = "Cache"         # NOTE: capital C
EXTENSIONS_BGSCRIPT_STATUS = "extensions-backgroundscript-status"
REFLOW = "reflow"
```

### Targets Enum

```python
class Targets(str, Enum):
    FRAME = "frame"
    PROCESS = "process"
    WORKER = "worker"       # covers web, service, and shared workers
```

## NetworkParentActor

| Method | Returns | Notes |
|---|---|---|
| `set_persist(enabled)` | `dict` | Keep events after navigation |
| `set_save_request_and_response_bodies(save)` | `dict` | **Required for response bodies** |
| `get_blocked_urls()` | `{urls: [str]}` | |
| `set_blocked_urls(urls)` | `dict` | |
| `set_network_throttling(download, upload, latency)` | `dict` | bytes/sec, ms |
| `get_network_throttling()` | `{state: {...}}` | |
| `clear_network_throttling()` | `dict` | |
| `block_request(filters)` | `dict` | |
| `unblock_request(filters)` | `dict` | |

## NetworkContentActor

Created from: `NetworkContentActor(client, target["networkContentActor"])`

| Method | Returns | Notes |
|---|---|---|
| `send_http_request(url, method="GET", headers=None, body="")` | `{channelId: int}` | Hardcodes `cause.type = "document"` |
| `get_stack_trace(resource_id)` | `dict` | Broken on Firefox 140+ |

## NetworkEventActor

Created from actor IDs in `resources-available-array` events.

| Method | Returns | Notes |
|---|---|---|
| `get_request_headers()` | `{headers: [{name, value}]}` | |
| `get_request_cookies()` | `{cookies: [...]}` | |
| `get_request_post_data()` | `{postData: {...}}` | or `{postDataDiscarded: true}` |
| `get_response_headers()` | `{headers: [{name, value}]}` | |
| `get_response_cookies()` | `{cookies: [...]}` | |
| `get_response_content()` | `{content: {mimeType, text}}` | Needs `set_save_request_and_response_bodies(True)` |
| `get_response_cache()` | `{cacheEntry: {...} \| null}` | |
| `get_event_timings()` | `{timings: {blocked, dns, connect, ssl, send, wait, receive}, totalTime}` | |
| `get_security_info()` | `{securityInfo: {...}}` | TLS details |
| `release()` | — | **Must call when done** to free memory |

Note: `getStackTrace` is spec-defined on NetworkEventActor but never implemented by Firefox.

## Live Traffic Capture Pattern

```python
watcher.watch_resources([Resources.NETWORK_EVENT])
net_parent.set_persist(True)
net_parent.set_save_request_and_response_bodies(True)

events = []
def on_event(msg):
    events.append(msg)

client.add_actor_listener(watcher.actor_id, on_event)
time.sleep(2)

for event in events:
    if event.get("type") == "resources-available-array":
        for res_type, items in event.get("array", []):
            if res_type == "network-event":
                for item in items:
                    net_event = NetworkEventActor(client, item["actor"])
                    headers = net_event.get_request_headers()
                    body = net_event.get_response_content()
                    net_event.release()
```
