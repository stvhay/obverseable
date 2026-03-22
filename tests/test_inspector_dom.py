"""Tests for InspectorActor, WalkerActor, NodeActor, NodeListActor — DOM inspection."""

from geckordp.actors.inspector import InspectorActor
from geckordp.actors.node import NodeActor
from geckordp.actors.node_list import NodeListActor
from geckordp.actors.walker import WalkerActor


class TestInspectorActor:
    def test_get_walker(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        result = inspector.get_walker()
        assert "actor" in result
        assert "root" in result
        assert result["root"]["nodeName"] == "#document"

    def test_get_page_style(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        result = inspector.get_page_style()
        assert result is not None

    def test_supports_highlighters(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        result = inspector.supports_highlighters()
        assert result is not None


class TestWalkerActor:
    def _get_walker(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        walker_resp = inspector.get_walker()
        return WalkerActor(client, walker_resp["actor"])

    def test_document(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        assert doc["nodeName"] == "#document"
        assert doc["nodeType"] == 9
        assert "actor" in doc
        assert "numChildren" in doc

    def test_children(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        children = walker.children(doc["actor"])
        assert isinstance(children, list)
        assert len(children) > 0
        # Should have at least HTML element
        node_names = [c["nodeName"] for c in children]
        assert "HTML" in node_names

    def test_query_selector_body(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        result = walker.query_selector(doc["actor"], "body")
        assert "node" in result
        assert result["node"]["nodeName"] == "BODY"

    def test_query_selector_all(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        result = walker.query_selector_all(doc["actor"], "div")
        assert "actor" in result
        assert "length" in result
        assert result["length"] > 0

    def test_search(self, client, target):
        walker = self._get_walker(client, target)
        result = walker.search("body")
        assert result is not None

    def test_inner_html_returns_longstring(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        body = walker.query_selector(doc["actor"], "body")
        html = walker.inner_html(body["node"]["actor"])
        # Large pages return LongString
        if isinstance(html, dict) and html.get("type") == "longString":
            assert "initial" in html
            assert "length" in html
            assert html["length"] > 0
        else:
            # Small pages may return string directly
            assert isinstance(html, (str, dict))

    def test_is_in_dom_tree(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        body = walker.query_selector(doc["actor"], "body")
        result = walker.is_in_dom_tree(body["node"]["actor"])
        assert result is not None

    def test_next_sibling(self, client, target):
        walker = self._get_walker(client, target)
        doc = walker.document()
        children = walker.children(doc["actor"])
        if len(children) > 1:
            result = walker.next_sibling(children[0]["actor"])
            assert result is not None

    def test_get_mutations(self, client, target):
        walker = self._get_walker(client, target)
        mutations = walker.get_mutations(cleanup=True)
        assert isinstance(mutations, list)


class TestNodeActor:
    def _get_body_node(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        walker_resp = inspector.get_walker()
        walker = WalkerActor(client, walker_resp["actor"])
        doc = walker.document()
        body = walker.query_selector(doc["actor"], "body")
        return NodeActor(client, body["node"]["actor"])

    def test_get_unique_selector(self, client, target):
        node = self._get_body_node(client, target)
        selector = node.get_unique_selector()
        assert isinstance(selector, str)
        assert len(selector) > 0

    def test_get_css_path(self, client, target):
        node = self._get_body_node(client, target)
        path = node.get_css_path()
        assert isinstance(path, str)

    def test_get_x_path(self, client, target):
        node = self._get_body_node(client, target)
        xpath = node.get_x_path()
        assert isinstance(xpath, str)
        assert xpath.startswith("/")

    def test_get_event_listener_info(self, client, target):
        node = self._get_body_node(client, target)
        events = node.get_event_listener_info()
        assert isinstance(events, list)


class TestNodeListActor:
    def test_item_and_items(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        walker_resp = inspector.get_walker()
        walker = WalkerActor(client, walker_resp["actor"])
        doc = walker.document()
        result = walker.query_selector_all(doc["actor"], "*")
        assert result["length"] > 0

        nodelist = NodeListActor(client, result["actor"])

        # Test single item
        first = nodelist.item(0)
        assert "node" in first

        # Test range
        batch = nodelist.items(0, min(3, result["length"]))
        assert "nodes" in batch
        assert len(batch["nodes"]) > 0

        nodelist.release()


class TestNodeObjectStructure:
    """Verify node objects have the documented fields."""

    def test_element_node_fields(self, client, target):
        inspector = InspectorActor(client, target["inspectorActor"])
        walker_resp = inspector.get_walker()
        walker = WalkerActor(client, walker_resp["actor"])
        doc = walker.document()
        body = walker.query_selector(doc["actor"], "body")
        node = body["node"]

        assert node["nodeType"] == 1  # ELEMENT_NODE
        assert node["nodeName"] == "BODY"
        assert "actor" in node
        assert "numChildren" in node
        assert "attrs" in node
        assert isinstance(node["attrs"], list)
