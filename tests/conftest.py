"""Shared fixtures for geckordp integration tests.

Requires Firefox running with:
    --start-debugger-server 6000
    devtools.debugger.remote-enabled = true
    devtools.debugger.force-local = false
    devtools.debugger.prompt-connection = false
    devtools.chrome.enabled = true
"""

import os

import pytest
from geckordp.actors.descriptors.tab import TabActor
from geckordp.actors.root import RootActor
from geckordp.rdp_client import RDPClient

FIREFOX_HOST = os.environ.get("FIREFOX_HOST", "192.168.64.1")
FIREFOX_PORT = int(os.environ.get("FIREFOX_PORT", "6000"))


@pytest.fixture(scope="module")
def client():
    """RDP client connected to Firefox. One per test module."""
    c = RDPClient(timeout_sec=5.0)
    c.connect(FIREFOX_HOST, FIREFOX_PORT)
    yield c
    c.disconnect()


@pytest.fixture(scope="module")
def root(client):
    """Root actor."""
    return RootActor(client)


@pytest.fixture(scope="module")
def tab_and_target(client, root):
    """First tab's TabActor and target dict."""
    tabs = root.list_tabs()
    assert len(tabs) > 0, "No tabs open in Firefox"
    tab_actor = TabActor(client, tabs[0]["actor"])
    target = tab_actor.get_target()
    return tab_actor, target


@pytest.fixture(scope="module")
def target(tab_and_target):
    """Target dict with all actor IDs."""
    return tab_and_target[1]


@pytest.fixture(scope="module")
def tab_actor(tab_and_target):
    """TabActor for the first tab."""
    return tab_and_target[0]
