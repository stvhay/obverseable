# StringActor — LongString Consumer

When `inner_html()` or `outer_html()` return large content, they produce a LongString:

```python
{
    "type": "longString",
    "actor": "server1.conn.../string42",
    "length": 271662,
    "initial": "...first ~4000 chars..."
}
```

The `initial` field contains a preview. To get the full content, use `StringActor`:

```python
from geckordp.actors.string import StringActor

long_str = walker.inner_html(body_actor)
if isinstance(long_str, dict) and long_str.get("type") == "longString":
    string_actor = StringActor(client, long_str["actor"])
    # Fetch in chunks
    full_content = ""
    chunk_size = 4000
    for start in range(0, long_str["length"], chunk_size):
        end = min(start + chunk_size, long_str["length"])
        chunk = string_actor.substring(start, end)
        full_content += chunk
```

## Method

| Method | Returns | Notes |
|---|---|---|
| `substring(start, end)` | `str` | Extracts `"substring"` field from response |
