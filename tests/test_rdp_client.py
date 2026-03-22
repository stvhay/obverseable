"""Tests for RDPClient connection, send/receive, and listener API."""

import time

from geckordp.rdp_client import RDPClient

from .conftest import FIREFOX_HOST, FIREFOX_PORT


class TestConnection:
    def test_connect_returns_greeting(self):
        client = RDPClient(timeout_sec=5.0)
        greeting = client.connect(FIREFOX_HOST, FIREFOX_PORT)
        assert greeting is not None
        assert greeting["from"] == "root"
        assert greeting["applicationType"] == "browser"
        assert "traits" in greeting
        client.disconnect()

    def test_connected_property(self):
        client = RDPClient(timeout_sec=5.0)
        assert not client.connected()
        client.connect(FIREFOX_HOST, FIREFOX_PORT)
        assert client.connected()
        client.disconnect()


class TestSendReceive:
    def test_send_receive_full_response(self, client):
        result = client.send_receive({"to": "root", "type": "listTabs"}, "")
        assert "tabs" in result
        assert "from" in result

    def test_send_receive_extract_field(self, client):
        tabs = client.send_receive(
            {"to": "root", "type": "listTabs"}, "tabs"
        )
        assert isinstance(tabs, list)
        assert len(tabs) > 0

    def test_send_receive_extract_nested(self, client):
        title = client.send_receive(
            {"to": "root", "type": "listTabs"}, "tabs[0].title"
        )
        assert isinstance(title, str)
        assert len(title) > 0

    def test_send_receive_error_response(self, client):
        result = client.send_receive(
            {"to": "root", "type": "nonExistentMethod"}, ""
        )
        assert result is not None
        assert "error" in result


class TestListeners:
    def test_actor_listener(self, client):
        received = []

        def handler(data):
            received.append(data)

        client.add_actor_listener("root", handler)
        client.send({"to": "root", "type": "listTabs"})
        time.sleep(0.5)
        client.remove_actor_listener("root", handler)

        assert len(received) > 0
        assert "tabs" in received[0]

    def test_universal_listener(self, client):
        received = []

        def handler(data):
            received.append(data)

        client.add_universal_listener(handler)
        client.send({"to": "root", "type": "listTabs"})
        time.sleep(0.5)
        client.remove_universal_listener(handler)

        assert len(received) > 0

    def test_duplicate_listener_returns_false(self, client):
        def handler(data):
            pass

        assert client.add_actor_listener("root", handler) is True
        assert client.add_actor_listener("root", handler) is False
        client.remove_actor_listener("root", handler)
