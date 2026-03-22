"""Tests for StringActor — LongString consumer for large DOM content."""

from geckordp.actors.inspector import InspectorActor
from geckordp.actors.string import StringActor
from geckordp.actors.walker import WalkerActor


class TestStringActor:
    def _get_longstring(self, client, target):
        """Get a LongString from inner_html of body."""
        inspector = InspectorActor(client, target["inspectorActor"])
        walker_resp = inspector.get_walker()
        walker = WalkerActor(client, walker_resp["actor"])
        doc = walker.document()
        body = walker.query_selector(doc["actor"], "body")
        return walker.inner_html(body["node"]["actor"])

    def test_inner_html_returns_longstring_or_str(self, client, target):
        result = self._get_longstring(client, target)
        # Could be a LongString dict or a plain string for small pages
        if isinstance(result, dict):
            assert result.get("type") == "longString"
            assert "actor" in result
            assert "length" in result
            assert "initial" in result

    def test_substring_fetches_content(self, client, target):
        result = self._get_longstring(client, target)
        if isinstance(result, dict) and result.get("type") == "longString":
            string_actor = StringActor(client, result["actor"])
            chunk = string_actor.substring(0, 100)
            assert isinstance(chunk, str)
            assert len(chunk) > 0
