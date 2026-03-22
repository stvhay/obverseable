"""
Reusable RDP recon utilities for black-box reverse engineering.

Usage:
    from tools.recon import RDPSession

    with RDPSession() as s:
        s.navigate("https://example.com")
        info = s.fingerprint()
        source = s.fetch_text("./app.js")
        sources = s.extract_source_map("./app.bundle.js")
        listeners = s.capture_event_listeners()
        traffic = s.capture_network(action="reload")
"""

import json
import os
import time
from contextlib import contextmanager

from geckordp.rdp_client import RDPClient
from geckordp.actors.root import RootActor
from geckordp.actors.descriptors.tab import TabActor
from geckordp.actors.targets.window_global import WindowGlobalActor
from geckordp.actors.web_console import WebConsoleActor
from geckordp.actors.inspector import InspectorActor
from geckordp.actors.walker import WalkerActor
from geckordp.actors.watcher import WatcherActor
from geckordp.actors.network_parent import NetworkParentActor
from geckordp.actors.network_event import NetworkEventActor
from geckordp.actors.resources import Resources


class RDPSession:
    """Manages an RDP connection with helpers for common RE operations."""

    def __init__(self, host=None, port=None, timeout=10.0):
        self.host = host or os.environ.get("FIREFOX_HOST", "192.168.64.1")
        self.port = int(port or os.environ.get("FIREFOX_PORT", "6000"))
        self.timeout = timeout
        self.client = None
        self.root = None
        self._target = None
        self._console_actor_id = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def connect(self):
        self.client = RDPClient(timeout_sec=self.timeout)
        self.client.connect(self.host, self.port)
        self.root = RootActor(self.client)
        self._acquire_target()

    def disconnect(self):
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

    def _acquire_target(self):
        """Get target actors from first tab."""
        tabs = self.root.list_tabs()
        tab_actor = TabActor(self.client, tabs[0]["actor"])
        self._target = tab_actor.get_target()
        self._console_actor_id = self._target["consoleActor"]
        self._tab_actor = tab_actor

    def navigate(self, url, wait=3.0):
        """Navigate to URL and re-acquire all actors."""
        window = WindowGlobalActor(self.client, self._target["actor"])
        window.navigate_to(url)
        time.sleep(wait)
        self._acquire_target()

    def reload(self, wait=3.0):
        """Reload current page and re-acquire actors."""
        window = WindowGlobalActor(self.client, self._target["actor"])
        window.reload()
        time.sleep(wait)
        self._acquire_target()

    # For addEventListener monkey-patching, use ScriptInjector from tools/inject.py.
    # It uses the debugger's script.source.firstStatement breakpoint to inject
    # JS before any page scripts run, surviving the navigation global swap.

    def eval_js(self, expr, wait=1.0):
        """Evaluate JS and return the result value. Handles two-stage async pattern.

        Returns the raw result value:
        - str/int/float/bool for primitives
        - dict for object grips (Promise, Array, etc.)
        - None on error
        """
        console = WebConsoleActor(self.client, self._console_actor_id)
        results = []

        def on_result(data):
            results.append(data)

        self.client.add_actor_listener(self._console_actor_id, on_result)
        console.evaluate_js_async(expr)
        time.sleep(wait)
        self.client.remove_actor_listener(self._console_actor_id, on_result)

        for r in results:
            if r.get("type") == "evaluationResult":
                if r.get("hasException"):
                    raise RuntimeError(r.get("exceptionMessage", "JS eval error"))
                return r.get("result")
        return None

    def eval_json(self, expr, wait=1.0):
        """Evaluate JS expression that returns a JSON string, parse and return dict.

        Handles LongString grips automatically — large JSON results (>1KB)
        from Firefox RDP are returned as LongString actors, not raw strings.
        """
        val = self.eval_js(expr, wait)
        val = self._resolve_long_string(val)
        if isinstance(val, str):
            return json.loads(val)
        return val

    def _resolve_long_string(self, val):
        """Resolve a LongString grip to full content string."""
        if not (isinstance(val, dict) and val.get("type") == "longString"):
            return val
        from geckordp.actors.string import StringActor
        actor = StringActor(self.client, val["actor"])
        full = ""
        chunk_size = 4000
        for start in range(0, val["length"], chunk_size):
            end = min(start + chunk_size, val["length"])
            full += actor.substring(start, end)
        return full

    def fetch_text(self, url, wait=2.0):
        """Fetch a URL from the page context and return text content.

        Uses the window.__tmp stash pattern to handle async fetch.
        Resolves LongString grips automatically.
        """
        self.eval_js(
            f'fetch("{url}").then(r=>r.text()).then(t=>{{window.__tmp=t}})', wait
        )
        val = self.eval_js("window.__tmp", 0.3)
        val = self._resolve_long_string(val)
        self.eval_js("delete window.__tmp", 0.1)
        return val

    def fingerprint(self):
        """Single-call page fingerprint. Returns dict with all surface-level info."""
        return self.eval_json(
            """JSON.stringify({
            url: location.href,
            title: document.title,
            charset: document.characterSet,
            contentType: document.contentType,
            doctype: document.doctype ? document.doctype.name : null,
            cookie: document.cookie,
            referrer: document.referrer,
            scripts: [...document.querySelectorAll("script")].map(s => ({
                src: s.src ? s.src.replace(location.origin, "") : null,
                type: s.type || "classic",
                len: s.textContent.length
            })),
            stylesheets: [...document.querySelectorAll("link[rel=stylesheet]")].map(l => l.href.replace(location.origin, "")),
            metas: [...document.querySelectorAll("meta")].map(m => ({
                name: m.name, content: m.content, httpEquiv: m.httpEquiv, charset: m.charset
            })).filter(m => m.name || m.content || m.httpEquiv || m.charset),
            frameworks: {
                react: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
                reactFiber: (() => {
                    const el = document.querySelector("#root, .todoapp, #app, [data-reactroot]");
                    return el ? Object.keys(el).some(k => k.startsWith("__reactFiber")) : false;
                })(),
                vue: !!window.__VUE__ || !!document.querySelector("[data-v-app]"),
                angular: !!window.ng || !!document.querySelector("[ng-version]"),
                svelte: !!window.__svelte,
                jquery: !!window.jQuery,
                backbone: !!window.Backbone
            },
            storage: {
                localStorageKeys: Object.keys(localStorage),
                sessionStorageKeys: Object.keys(sessionStorage),
                cookieCount: document.cookie ? document.cookie.split(";").length : 0
            },
            links: [...document.querySelectorAll("a[href]")].slice(0, 50).map(a => ({
                text: a.textContent.trim().slice(0, 80),
                href: a.href
            })),
            interactive: {
                buttons: [...document.querySelectorAll("button, [role=button]")].slice(0, 50).map(b => ({
                    text: b.textContent.trim().slice(0, 60),
                    type: b.type || null,
                    ariaLabel: b.getAttribute("aria-label"),
                    id: b.id || null,
                    classes: b.className ? b.className.split(" ").slice(0, 3).join(" ") : null
                })),
                inputs: [...document.querySelectorAll("input, textarea, select")].slice(0, 30).map(i => ({
                    type: i.type || i.tagName.toLowerCase(),
                    name: i.name || null,
                    placeholder: i.placeholder || null,
                    ariaLabel: i.getAttribute("aria-label"),
                    id: i.id || null
                })),
                nav: [...document.querySelectorAll("nav, [role=navigation], [role=tablist]")].slice(0, 10).map(n => ({
                    tag: n.tagName,
                    ariaLabel: n.getAttribute("aria-label"),
                    items: [...n.querySelectorAll("a, button, [role=tab]")].slice(0, 10).map(i => i.textContent.trim().slice(0, 40))
                })),
                details: [...document.querySelectorAll("details, [role=menu]")].slice(0, 20).map(d => ({
                    summary: d.querySelector("summary")?.textContent?.trim()?.slice(0, 60) || d.getAttribute("aria-label"),
                    open: d.open || false
                })),
                dialogs: [...document.querySelectorAll("dialog, [role=dialog]")].map(d => ({
                    id: d.id || null,
                    ariaLabel: d.getAttribute("aria-label"),
                    open: d.open || d.hasAttribute("open")
                }))
            }
        })""",
            wait=1.5,
        )

    def extract_source_map(self, bundle_url):
        """Fetch a JS bundle and its source map. Returns dict of {filepath: content}.

        Returns None if no source map found.
        Handles large bundles and source maps via LongString resolution.
        For very large source maps (>500KB), parses in-browser to avoid
        transferring the full map to Python.
        """
        # Check for source map URL without fetching full bundle
        has_map = self.eval_json(
            f'''(() => {{
                window.__sm_check = null;
                return JSON.stringify({{checking: true}});
            }})()'''
        )
        self.eval_js(
            f'fetch("{bundle_url}").then(r=>r.text()).then(t=>{{window.__sm_check=t}})',
            wait=3.0,
        )
        check = self.eval_json(
            '''JSON.stringify({
                size: window.__sm_check ? window.__sm_check.length : -1,
                hasMap: window.__sm_check ? window.__sm_check.includes("sourceMappingURL") : false,
                mapUrl: window.__sm_check ? (window.__sm_check.match(/sourceMappingURL=(.+)$/m) || [])[1] || null : null
            })'''
        )

        if not check or check.get("size", -1) < 0:
            self.eval_js("delete window.__sm_check", 0.1)
            return None

        if not check.get("hasMap"):
            # No source map — fetch the bundle text directly
            source = self._resolve_long_string(
                self.eval_js("window.__sm_check", 0.3)
            )
            self.eval_js("delete window.__sm_check", 0.1)
            return {"__bundle__": source} if isinstance(source, str) else None

        map_url = check["mapUrl"]
        self.eval_js("delete window.__sm_check", 0.1)

        if not map_url:
            return None

        # Fetch and parse source map in-browser to avoid LongString transfer
        self.eval_js(
            f'fetch("{map_url}").then(r=>r.text()).then(t=>{{window.__sm_data=JSON.parse(t)}})',
            wait=5.0,
        )

        # Get source file list
        sources_val = self.eval_js(
            "JSON.stringify(window.__sm_data ? window.__sm_data.sources : [])", wait=1.0
        )
        sources_val = self._resolve_long_string(sources_val)
        if not isinstance(sources_val, str):
            self.eval_js("delete window.__sm_data", 0.1)
            return None
        sources_list = json.loads(sources_val)

        # Extract each source file content
        result = {}
        for i, src_path in enumerate(sources_list):
            content = self.eval_js(
                f"window.__sm_data.sourcesContent[{i}]", wait=0.5
            )
            content = self._resolve_long_string(content)
            if isinstance(content, str) and len(content) > 0:
                result[src_path] = content

        self.eval_js("delete window.__sm_data", 0.1)
        return result

    def walk_dom(self, selector=None, max_depth=3):
        """Walk the DOM tree and return a nested structure.

        If selector is given, starts from that element. Otherwise from document root.
        """
        inspector = InspectorActor(self.client, self._target["inspectorActor"])
        walker_resp = inspector.get_walker()
        walker = WalkerActor(self.client, walker_resp["actor"])
        doc_root = walker_resp["root"]

        if selector:
            result = walker.query_selector(doc_root["actor"], selector)
            start_node = result.get("node", result)
        else:
            start_node = doc_root

        def walk(node, depth=0):
            attrs = node.get("attrs", [])
            info = {
                "tag": node.get("nodeName", "?"),
                "type": node.get("nodeType"),
                "attrs": {a["name"]: a["value"] for a in attrs} if attrs else {},
            }
            if depth < max_depth and node.get("numChildren", 0) > 0:
                children = walker.children(node["actor"])
                info["children"] = [walk(c, depth + 1) for c in children if c.get("nodeType") == 1]
            return info

        return walk(start_node)

    def extract_styles(self, selectors):
        """Extract computed styles for a list of CSS selectors. Returns list of dicts."""
        sel_json = json.dumps(selectors)
        return self.eval_json(
            f"""JSON.stringify({sel_json}.map(sel => {{
                const el = document.querySelector(sel);
                if (!el) return {{selector: sel, found: false}};
                const cs = getComputedStyle(el);
                return {{
                    selector: sel, found: true, tag: el.tagName,
                    color: cs.color, backgroundColor: cs.backgroundColor,
                    fontFamily: cs.fontFamily, fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight, lineHeight: cs.lineHeight,
                    width: cs.width, maxWidth: cs.maxWidth, minWidth: cs.minWidth,
                    height: cs.height, padding: cs.padding, margin: cs.margin,
                    border: cs.border, borderRadius: cs.borderRadius,
                    boxShadow: cs.boxShadow, textDecoration: cs.textDecoration,
                    display: cs.display, position: cs.position,
                    opacity: cs.opacity, transform: cs.transform,
                    outline: cs.outline, cursor: cs.cursor
                }};
            }}))""",
            wait=1.0,
        )

    def fetch_css_sources(self):
        """Fetch all linked stylesheet sources. Returns list of {href, content} dicts."""
        hrefs = self.eval_json(
            'JSON.stringify([...document.querySelectorAll("link[rel=stylesheet]")].map(l => l.href))'
        )
        if not hrefs:
            return []
        results = []
        for href in hrefs:
            content = self.fetch_text(href, wait=2.0)
            if isinstance(content, str) and len(content) > 0:
                results.append({"href": href, "content": content})
        return results

    def classify_scripts(self):
        """Classify all loaded scripts by role. Returns list of dicts with src, role, size."""
        return self.eval_json(
            """JSON.stringify([...document.querySelectorAll("script")].map(s => {
                const src = s.src ? s.src.replace(location.origin, "") : null;
                let role = "unknown";
                if (!src) role = "inline";
                else if (src.includes("analytics") || src.includes("ga.js") || src.includes("gtag")) role = "analytics";
                else if (src.includes("node_modules") || src.includes("bower_components")) role = "dependency";
                else if (src.includes("polyfill") || src.includes("webcomponent") || src.includes("prefixfree")) role = "polyfill";
                else if (src.includes("bundle") || src.includes("app.")) role = "app";
                else if (src.includes("base.") || src.includes("common")) role = "shared-infra";
                else if (src.includes("twitter") || src.includes("facebook") || src.includes("plusone") || src.includes("widget")) role = "social";
                else role = "app";
                return {src, role, type: s.type || "classic", len: s.textContent.length};
            }))""",
            wait=1.0,
        )

    def capture_network(self, action=None, wait=5.0):
        """Capture network traffic. If action is 'reload', reloads the page.

        Returns list of request dicts.
        """
        watcher_resp = self._tab_actor.get_watcher()
        watcher = WatcherActor(self.client, watcher_resp["actor"])
        watcher.watch_resources([Resources.NETWORK_EVENT])

        net_parent_resp = watcher.get_network_parent_actor()
        net_parent = NetworkParentActor(
            self.client, net_parent_resp["network"]["actor"]
        )
        net_parent.set_persist(True)
        net_parent.set_save_request_and_response_bodies(True)

        events = []

        def on_event(msg):
            events.append(msg)

        self.client.add_actor_listener(watcher.actor_id, on_event)

        if action == "reload":
            window = WindowGlobalActor(self.client, self._target["actor"])
            window.reload()

        time.sleep(wait)
        self.client.remove_actor_listener(watcher.actor_id, on_event)

        # Merge available (request start) and updated (response complete) events
        requests_by_actor = {}
        for event in events:
            event_type = event.get("type", "")
            if event_type not in ("resources-available-array", "resources-updated-array"):
                continue
            for res_type_items in event.get("array", []):
                if not (isinstance(res_type_items, (list, tuple)) and len(res_type_items) == 2):
                    continue
                res_type, items = res_type_items
                if res_type != "network-event":
                    continue
                for item in items:
                    actor_id = item.get("actor") or item.get("resourceId")
                    if not actor_id:
                        continue
                    if actor_id not in requests_by_actor:
                        requests_by_actor[actor_id] = {}
                    requests_by_actor[actor_id].update({
                        k: v for k, v in item.items()
                        if v is not None and k != "actor" and k != "resourceId"
                    })
                    requests_by_actor[actor_id]["_actor"] = actor_id

        # Re-acquire target BEFORE querying network actors, since reload
        # invalidates the old window global but network event actors may
        # still be valid on the new context.
        if action == "reload":
            self._acquire_target()

        requests = []
        for actor_id, data in requests_by_actor.items():
            req = {
                "url": data.get("url"),
                "method": data.get("method"),
                "status": data.get("status") or data.get("statusCode"),
                "mimeType": data.get("mimeType"),
                "contentSize": data.get("contentSize") or data.get("transferredSize"),
            }
            # Network event actors from resource events may be stale after
            # reload — use a short timeout and skip on failure rather than
            # hanging for the default 10s per request.
            try:
                ne = NetworkEventActor(self.client, actor_id)
                old_timeout = self.client.timeout_sec
                self.client.timeout_sec = 2.0
                try:
                    timings = ne.get_event_timings()
                    req["totalTime"] = timings.get("totalTime")
                    headers = ne.get_response_headers()
                    req["responseHeaders"] = {
                        h["name"]: h["value"]
                        for h in headers.get("headers", [])
                    }
                    ne.release()
                except Exception:
                    pass
                finally:
                    self.client.timeout_sec = old_timeout
            except Exception:
                pass
            requests.append(req)

        return requests


def write_json(data, path):
    """Write data as formatted JSON to path, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def write_sources(sources_dict, output_dir):
    """Write extracted source files to output directory."""
    os.makedirs(output_dir, exist_ok=True)
    for filepath, content in sources_dict.items():
        if not isinstance(content, str):
            continue
        # Normalize webpack:// paths
        clean = filepath
        for prefix in ["webpack://", "webpack:///"]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
        # Remove leading slashes, keep relative structure
        clean = clean.lstrip("/")
        # Skip node_modules
        if "node_modules/" in clean:
            continue
        out_path = os.path.join(output_dir, clean)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(content)
