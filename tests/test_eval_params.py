"""Tests for evaluate_js_async advanced parameters found by audit."""

import time

from geckordp.actors.web_console import WebConsoleActor


def _eval_and_wait(client, console, expression, timeout=1.0, **kwargs):
    results = []

    def on_result(data):
        results.append(data)

    client.add_actor_listener(console.actor_id, on_result)
    console.evaluate_js_async(expression, **kwargs)
    time.sleep(timeout)
    client.remove_actor_listener(console.actor_id, on_result)
    return [r for r in results if r.get("type") == "evaluationResult"]


class TestEagerEval:
    def test_eager_simple_expression(self, client, target):
        """Eager eval should work for side-effect-free expressions."""
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(client, console, "2 + 2", eager=True)
        assert len(results) == 1
        assert results[0]["result"] == 4


class TestInnerWindowId:
    def test_default_inner_window(self, client, target):
        """Passing inner_window_id=-1 should use default (top-level)."""
        console = WebConsoleActor(client, target["consoleActor"])
        results = _eval_and_wait(
            client, console, "document.title", inner_window_id=-1
        )
        assert len(results) == 1
        assert isinstance(results[0]["result"], str)
