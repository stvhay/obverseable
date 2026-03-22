"""Tests for network actors — WatcherActor, NetworkParentActor, NetworkContentActor."""

import time

from geckordp.actors.network_content import NetworkContentActor
from geckordp.actors.network_event import NetworkEventActor
from geckordp.actors.network_parent import NetworkParentActor
from geckordp.actors.resources import Resources
from geckordp.actors.watcher import WatcherActor


class TestWatcherActor:
    def _get_watcher(self, client, tab_actor):
        resp = tab_actor.get_watcher()
        return WatcherActor(client, resp["actor"])

    def test_watch_resources(self, client, tab_actor):
        watcher = self._get_watcher(client, tab_actor)
        result = watcher.watch_resources([Resources.NETWORK_EVENT])
        assert result is not None
        watcher.unwatch_resources([Resources.NETWORK_EVENT])

    def test_get_network_parent_actor(self, client, tab_actor):
        watcher = self._get_watcher(client, tab_actor)
        result = watcher.get_network_parent_actor()
        assert "network" in result
        assert "actor" in result["network"]


class TestNetworkParentActor:
    def _setup_network(self, client, tab_actor):
        watcher_resp = tab_actor.get_watcher()
        watcher = WatcherActor(client, watcher_resp["actor"])
        watcher.watch_resources([Resources.NETWORK_EVENT])
        net_resp = watcher.get_network_parent_actor()
        net_parent = NetworkParentActor(client, net_resp["network"]["actor"])
        return watcher, net_parent

    def test_set_persist(self, client, tab_actor):
        watcher, net_parent = self._setup_network(client, tab_actor)
        result = net_parent.set_persist(True)
        assert result is not None
        watcher.unwatch_resources([Resources.NETWORK_EVENT])

    def test_set_save_bodies(self, client, tab_actor):
        watcher, net_parent = self._setup_network(client, tab_actor)
        result = net_parent.set_save_request_and_response_bodies(True)
        assert result is not None
        watcher.unwatch_resources([Resources.NETWORK_EVENT])

    def test_get_blocked_urls(self, client, tab_actor):
        watcher, net_parent = self._setup_network(client, tab_actor)
        result = net_parent.get_blocked_urls()
        assert "urls" in result
        assert isinstance(result["urls"], list)
        watcher.unwatch_resources([Resources.NETWORK_EVENT])

    def test_throttling(self, client, tab_actor):
        watcher, net_parent = self._setup_network(client, tab_actor)

        # Set throttling
        result = net_parent.set_network_throttling(10000, 5000, 100)
        assert result is not None

        # Get throttling
        state = net_parent.get_network_throttling()
        assert state is not None

        # Clear throttling
        result = net_parent.clear_network_throttling()
        assert result is not None

        watcher.unwatch_resources([Resources.NETWORK_EVENT])


class TestNetworkContentActor:
    def test_send_http_request(self, client, target, tab_actor):
        # Set up watcher first
        watcher_resp = tab_actor.get_watcher()
        watcher = WatcherActor(client, watcher_resp["actor"])
        watcher.watch_resources([Resources.NETWORK_EVENT])
        net_resp = watcher.get_network_parent_actor()
        net_parent = NetworkParentActor(client, net_resp["network"]["actor"])
        net_parent.set_save_request_and_response_bodies(True)

        net_content = NetworkContentActor(client, target["networkContentActor"])

        # Capture events
        events = []

        def on_event(msg):
            events.append(msg)

        client.add_actor_listener(watcher.actor_id, on_event)

        result = net_content.send_http_request("https://httpbin.org/get")
        assert result is not None

        # Wait for request to complete
        time.sleep(3)
        client.remove_actor_listener(watcher.actor_id, on_event)

        # Find network events
        net_events = []
        for event in events:
            if event.get("type") == "resources-available-array":
                for res_type, items in event.get("array", []):
                    if res_type == "network-event":
                        net_events.extend(items)

        assert len(net_events) > 0, "No network events captured"

        # Test NetworkEventActor on first event
        net_event = NetworkEventActor(client, net_events[0]["actor"])
        headers = net_event.get_request_headers()
        assert "headers" in headers
        assert isinstance(headers["headers"], list)

        timings = net_event.get_event_timings()
        assert "timings" in timings

        net_event.release()
        watcher.unwatch_resources([Resources.NETWORK_EVENT])
