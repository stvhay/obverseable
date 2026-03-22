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
        """Evaluate JS expression that returns a JSON string, parse and return dict."""
        val = self.eval_js(expr, wait)
        if isinstance(val, str):
            return json.loads(val)
        return val

    def fetch_text(self, url, wait=2.0):
        """Fetch a URL from the page context and return text content.

        Uses the window.__tmp stash pattern to handle async fetch.
        """
        self.eval_js(
            f'fetch("{url}").then(r=>r.text()).then(t=>{{window.__tmp=t}})', wait
        )
        val = self.eval_js("window.__tmp", 0.3)
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
            }))
        })""",
            wait=1.5,
        )

    def extract_source_map(self, bundle_url):
        """Fetch a JS bundle and its source map. Returns dict of {filepath: content}.

        Returns None if no source map found.
        """
        source = self.fetch_text(bundle_url, wait=2.0)
        if not source:
            return None

        # Check for sourceMappingURL
        if "sourceMappingURL=" not in source:
            return {"__bundle__": source}

        map_url = source.split("sourceMappingURL=")[-1].strip()
        map_text = self.fetch_text(map_url, wait=3.0)
        if not map_text:
            return {"__bundle__": source}

        sm = json.loads(map_text)
        result = {}
        sources = sm.get("sources", [])
        contents = sm.get("sourcesContent", [])
        for i, src_path in enumerate(sources):
            content = contents[i] if i < len(contents) else None
            if content:
                result[src_path] = content

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

        requests = []
        for actor_id, data in requests_by_actor.items():
            req = {
                "url": data.get("url"),
                "method": data.get("method"),
                "status": data.get("status") or data.get("statusCode"),
                "mimeType": data.get("mimeType"),
                "contentSize": data.get("contentSize") or data.get("transferredSize"),
            }
            try:
                ne = NetworkEventActor(self.client, actor_id)
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
            requests.append(req)

        # Re-acquire target since reload may have invalidated actors
        if action == "reload":
            self._acquire_target()

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
