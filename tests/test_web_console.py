"""Tests for WebConsoleActor — JS eval, cached messages, listeners."""

import time

from geckordp.actors.web_console import WebConsoleActor


def _eval_and_wait(client, console, expression, timeout=1.0):
    """Evaluate JS and collect async results. Returns list of evaluationResult dicts."""
    results = []

    def on_result(data):
        results.append(data)

    client.add_actor_listener(console.actor_id, on_result)
    console.evaluate_js_async(expression)
    time.sleep(timeout)
    client.remove_actor_listener(console.actor_id, on_result)

    return [r for r in results if r.get("type") == "evaluationResult"]


class TestEvaluateJsAsync:
    def test_simple_string(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(client, console, "document.title")
        assert len(results) == 1
        assert results[0]["hasException"] is False
        assert isinstance(results[0]["result"], str)
        assert len(results[0]["result"]) > 0

    def test_number(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(client, console, "2 + 2")
        assert len(results) == 1
        assert results[0]["result"] == 4

    def test_json_object(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(
            client, console, 'JSON.stringify({a: 1, b: "hello"})'
        )
        assert len(results) == 1
        assert '"a":1' in results[0]["result"]

    def test_location_href(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(client, console, "window.location.href")
        assert len(results) == 1
        assert results[0]["result"].startswith("http")

    def test_exception(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(
            client, console, 'throw new Error("test error")'
        )
        assert len(results) == 1
        assert results[0]["hasException"] is True

    def test_dom_query(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(
            client, console, "document.querySelectorAll('*').length"
        )
        assert len(results) == 1
        assert isinstance(results[0]["result"], int)
        assert results[0]["result"] > 0

    def test_result_has_timestamps(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(client, console, "'hello'")
        assert len(results) == 1
        assert "startTime" in results[0]
        assert "timestamp" in results[0]

    def test_result_id_correlation(self, client, target):
        """The immediate response and async result share the same resultID."""
        console = WebConsoleActor(client, target["consoleActor"])
        all_messages = []

        def on_msg(data):
            all_messages.append(data)

        client.add_actor_listener(target["consoleActor"], on_msg)
        console.evaluate_js_async("42")
        time.sleep(0.5)
        client.remove_actor_listener(target["consoleActor"], on_msg)

        # Should have at least 2 messages: immediate + result
        immediate = [m for m in all_messages if "resultID" in m and "type" not in m]
        results = [m for m in all_messages if m.get("type") == "evaluationResult"]
        assert len(immediate) >= 1
        assert len(results) >= 1
        assert immediate[0]["resultID"] == results[0]["resultID"]


class TestCachedMessages:
    def test_console_api(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        result = console.get_cached_messages(
            [WebConsoleActor.MessageTypes.CONSOLE_API]
        )
        # Returns dict with 'messages' key
        if isinstance(result, dict):
            assert "messages" in result
            assert isinstance(result["messages"], list)
        else:
            assert isinstance(result, list)

    def test_page_error(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        result = console.get_cached_messages(
            [WebConsoleActor.MessageTypes.PAGE_ERROR]
        )
        if isinstance(result, dict):
            assert "messages" in result
            assert isinstance(result["messages"], list)
        else:
            assert isinstance(result, list)


class TestAutocomplete:
    def test_document_prefix(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        result = console.autocomplete("document.titl", cursor=14)
        assert result is not None


class TestListeners:
    def test_start_stop_listeners(self, client, target):
        console = WebConsoleActor(client, target["consoleActor"])
        start_result = console.start_listeners(
            [WebConsoleActor.Listeners.CONSOLE_API]
        )
        assert start_result is not None

        stop_result = console.stop_listeners(
            [WebConsoleActor.Listeners.CONSOLE_API]
        )
        assert stop_result is not None
