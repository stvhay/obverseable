# RDPClient

```python
from geckordp.rdp_client import RDPClient

RDPClient(timeout_sec=3.0, max_buffer_size=33554432, executor_workers=3, executor=None)
```

- `timeout_sec`: response timeout in seconds
- `max_buffer_size`: max read buffer (~33MB default, needed for screenshots)
- `executor_workers`: thread pool size for event handlers
- `executor`: custom `ThreadPoolExecutor` to share across connections

## Methods

| Method | Returns | Notes |
|---|---|---|
| `connect(host, port)` | `dict` (greeting) | Returns root traits |
| `disconnect()` | `None` | |
| `connected()` | `bool` | |
| `send(msg)` | `bool` | Fire-and-forget, no response wait |
| `send_receive(msg, extract_expression="")` | `dict \| None` | Blocking. `None` on timeout. JMESPath extract. |
| `timeout_sec` | `float` (property) | Read-only |

## Listeners

| Method | Triggers on |
|---|---|
| `add_actor_listener(actor_id, handler)` | ALL responses from that actor |
| `remove_actor_listener(actor_id, handler)` | |
| `add_event_listener(actor_id, event, handler)` | Responses with matching `type` field |
| `remove_event_listener(actor_id, event, handler)` | |
| `remove_event_listeners_by_id(actor_id)` | All events for that actor |
| `add_universal_listener(handler)` | ALL responses from ALL actors |
| `remove_universal_listener(handler)` | |

Handler signature: `def handler(data: dict) -> None`

## Threading Model

RDPClient runs its own asyncio event loop on a background thread. Critical constraints:

- **Async handlers CANNOT call `send_receive()`** — it would block the event loop thread, causing deadlock.
- Use sync handlers if you need to make requests in response to events.
- `send_receive()` detects which thread it's called from and routes accordingly.

## JMESPath Extract

```python
client.send_receive({"to": "root", "type": "listTabs"}, "")           # full response
client.send_receive({"to": "root", "type": "listTabs"}, "tabs")       # extract field
client.send_receive({"to": "root", "type": "listTabs"}, "tabs[0].title")  # nested
```

If extract yields `None`, full response is returned as fallback.

## Error Handling

- `send_receive()` returns `None` on timeout (not an exception)
- Error responses are dicts with `"error"` key — always check
- `send()` raises `ValueError` if message lacks `"to"` field

## Bulk Responses

Large responses (heap snapshots) arrive as bulk packets, auto-converted to dicts with keys: `type`, `data` (base64), `data-size`, `data-decoded-size`, `data-encoding`, `from`.
