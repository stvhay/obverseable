"""
Early script injection via Firefox RDP.

Injects JavaScript before any page scripts execute by using the debugger's
`script.source.firstStatement` event breakpoint. This is Firefox RDP's
equivalent of CDP's `Page.addScriptToEvaluateOnNewDocument`.

Usage:
    from tools.inject import ScriptInjector

    with RDPSession() as s:
        injector = ScriptInjector(s.client, s._tab_actor, session=s)

        # Inject arbitrary JS before page scripts run
        injector.navigate("https://example.com", '''
            window.__injected = true;
        ''')
        # s.eval_js() works — session actors refreshed automatically
        print(s.eval_js("window.__injected"))  # True

        # High-level: capture all addEventListener calls
        listeners = injector.capture_event_listeners("https://example.com")
        # => [{"target": "BUTTON", "id": "submit", "type": "click", ...}, ...]

Mechanism:
    1. Watcher-level breakpoint list sets `script.source.firstStatement`
    2. Watcher watches FRAME targets with server target switching
    3. On target-available, thread attaches with the event breakpoint
    4. Thread pauses before first JS statement executes
    5. evaluateJS injects the script while paused
    6. Breakpoint cleared and thread resumed — page runs with injection active
"""

import json
import threading
import time

from geckordp.actors.descriptors.tab import TabActor
from geckordp.actors.events import Events
from geckordp.actors.targets.window_global import WindowGlobalActor
from geckordp.actors.thread import ThreadActor
from geckordp.actors.watcher import WatcherActor
from geckordp.actors.web_console import WebConsoleActor
from geckordp.rdp_client import RDPClient

_AEL_MONKEY_PATCH = """\
(function() {
    if (window.__ael_log) return;
    window.__ael_log = [];
    var orig = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, fn, opts) {
        var tag = '?';
        try { tag = this.tagName || this.constructor.name; } catch(e) {}
        window.__ael_log.push({
            target: tag,
            id: this.id || '',
            className: this.className || '',
            type: type,
            capture: !!(opts && (opts.capture || opts === true)),
            timestamp: Date.now()
        });
        return orig.call(this, type, fn, opts);
    };
    window.__ael_patched = true;
})();
void(0);
"""


class ScriptInjector:
    """Injects JavaScript before page scripts execute via RDP debugger pause.

    If constructed with an RDPSession, refreshes the session's actors after
    each navigation so eval_js() etc. continue to work.
    """

    def __init__(self, client: RDPClient, tab_actor: TabActor, session=None):
        self.client = client
        self.tab_actor = tab_actor
        self._session = session
        self._watcher = None
        self._watcher_id = None
        self._bp_list_id = None
        self._thread_config_id = None
        self._setup_done = False

    def _setup_watcher(self):
        """One-time watcher setup with breakpoint list and thread config."""
        if self._setup_done:
            return

        watcher_resp = self.tab_actor.get_watcher(
            is_server_target_switching_enabled=True
        )
        self._watcher_id = watcher_resp["actor"]
        self._watcher = WatcherActor(self.client, self._watcher_id)

        # Breakpoint list actor — sets breakpoints applied to all new targets
        bp_resp = self._watcher.get_breakpoint_list_actor()
        self._bp_list_id = bp_resp["breakpointList"]["actor"]

        # Thread config — ensures threads are configured to honor breakpoints
        tc_resp = self._watcher.get_thread_configuration_actor()
        self._thread_config_id = tc_resp["actor"]
        self.client.send_receive(
            {
                "to": self._thread_config_id,
                "type": "updateConfiguration",
                "configuration": {
                    "pauseOnExceptions": False,
                    "ignoreCaughtExceptions": True,
                    "skipBreakpoints": False,
                    "logEventBreakpoints": False,
                },
            }
        )

        self._setup_done = True

    def _set_first_statement_breakpoint(self, enabled: bool):
        ids = ["script.source.firstStatement"] if enabled else []
        self.client.send_receive(
            {
                "to": self._bp_list_id,
                "type": "setActiveEventBreakpoints",
                "ids": ids,
            }
        )

    def navigate(self, url: str, script: str, wait: float = 3.0) -> dict:
        """Navigate to url, injecting script before any page JS runs.

        Returns the new target dict (with threadActor, consoleActor, etc).
        """
        self._setup_watcher()

        # Navigate away first if already on the target URL — same-page navigation
        # doesn't create a new target, so the breakpoint never fires.
        if self._session is not None:
            current = self._session.eval_js("location.href", wait=0.3)
            if current == url:
                current_target = self.tab_actor.get_target()
                w = WindowGlobalActor(self.client, current_target["actor"])
                w.navigate_to("about:blank")
                time.sleep(0.5)

        self._set_first_statement_breakpoint(True)

        # State shared with the target-available callback
        paused = threading.Event()
        new_target = {}

        def on_target_available(data):
            t = data.get("target", {})
            if not t.get("isTopLevelTarget"):
                return
            new_target.update(t)
            thread_id = t.get("threadActor", "")
            if not thread_id:
                return

            def on_pause(pdata):
                if pdata.get("why", {}).get("type") == "eventBreakpoint":
                    paused.set()

            self.client.add_event_listener(
                thread_id, Events.Thread.PAUSED, on_pause
            )
            thread = ThreadActor(self.client, thread_id)
            thread.attach(event_breakpoints=["script.source.firstStatement"])

        self.client.add_event_listener(
            self._watcher_id,
            Events.Watcher.TARGET_AVAILABLE_FORM,
            on_target_available,
        )

        # Start watching targets, then navigate
        self._watcher.watch_targets(WatcherActor.Targets.FRAME)
        time.sleep(0.3)

        # Get current target to issue navigation
        current_target = self.tab_actor.get_target()
        window = WindowGlobalActor(self.client, current_target["actor"])
        window.navigate_to(url)

        if not paused.wait(timeout=15):
            # Clean up and fall through — page loaded without pausing
            self._set_first_statement_breakpoint(False)
            self.client.remove_event_listener(
                self._watcher_id,
                Events.Watcher.TARGET_AVAILABLE_FORM,
                on_target_available,
            )
            return new_target

        # Paused on first statement — inject the script
        console = WebConsoleActor(self.client, new_target["consoleActor"])
        eval_done = threading.Event()
        eval_ok = [False]

        def on_eval(data):
            if data.get("type") == "evaluationResult":
                eval_ok[0] = not data.get("hasException", True)
                eval_done.set()

        self.client.add_actor_listener(new_target["consoleActor"], on_eval)
        console.evaluate_js_async(script)
        eval_done.wait(timeout=5)
        self.client.remove_actor_listener(new_target["consoleActor"], on_eval)

        # Clear breakpoint so remaining scripts run freely, then resume
        self._set_first_statement_breakpoint(False)
        thread = ThreadActor(self.client, new_target["threadActor"])
        try:
            thread.resume()
        except Exception:
            pass

        self.client.remove_event_listener(
            self._watcher_id,
            Events.Watcher.TARGET_AVAILABLE_FORM,
            on_target_available,
        )

        time.sleep(wait)

        if self._session is not None:
            self._session._acquire_target()

        return new_target

    def _resolve_long_string(self, val):
        """Resolve a LongString grip to full content."""
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

    def capture_event_listeners(self, url: str, wait: float = 3.0) -> list[dict]:
        """Navigate to url, capturing every addEventListener call.

        Returns list of dicts: {target, id, className, type, capture, timestamp}.
        """
        self.navigate(url, _AEL_MONKEY_PATCH, wait=wait)

        # Use the session's refreshed actors (navigate calls _acquire_target)
        if self._session is not None:
            val = self._session.eval_js(
                "JSON.stringify(window.__ael_log || [])"
            )
            val = self._resolve_long_string(val)
            if isinstance(val, str):
                return json.loads(val)
            return val if isinstance(val, list) else []

        # Fallback: no session, use tab_actor to get fresh target
        target = self.tab_actor.get_target()
        console = WebConsoleActor(self.client, target["consoleActor"])
        results = []

        def on_result(data):
            results.append(data)

        self.client.add_actor_listener(target["consoleActor"], on_result)
        console.evaluate_js_async(
            "JSON.stringify(window.__ael_log || [])"
        )
        time.sleep(1)
        self.client.remove_actor_listener(target["consoleActor"], on_result)

        for r in results:
            if r.get("type") == "evaluationResult" and not r.get("hasException"):
                val = r.get("result", "[]")
                val = self._resolve_long_string(val)
                if isinstance(val, str):
                    return json.loads(val)
        return []
